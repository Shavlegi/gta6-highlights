#!/usr/bin/env python3
"""Build a highlight cut list from a video file using ffmpeg scene detection.

Runs entirely in CI: no human watches the video. Scene-change timestamps are
grouped into segments of roughly 75-150 seconds, so cuts land on real visual
breaks instead of arbitrary times. If scene detection finds too few cuts, the
script falls back to even splits so the job always yields 20+ clips.

Usage: python3 make_cutlist.py video.mp4 cutlist.json
"""
import json
import re
import subprocess
import sys

SCENE_THRESHOLD = 0.4   # ffmpeg scene-change sensitivity (0.0-1.0)
MIN_SEG = 75.0          # shortest segment (seconds)
MAX_SEG = 180.0         # longest segment before a forced cut
FORCE_SEG = 120.0       # forced-cut step inside long unbroken stretches
MIN_CLIPS = 20          # guaranteed minimum clip count
EVEN_CLIPS = 24         # clip count for the even-split fallback


def probe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", path],
        capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def scene_boundaries(path):
    """Return sorted scene-change timestamps (seconds) from ffmpeg showinfo."""
    cmd = ["ffmpeg", "-hide_banner", "-i", path, "-filter:v",
           "select='gt(scene,%s)',showinfo" % SCENE_THRESHOLD,
           "-vsync", "vfr", "-f", "null", "-"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    times = []
    for line in proc.stderr.splitlines():
        m = re.search(r"showinfo.*pts_time:([0-9.]+)", line)
        if m:
            times.append(float(m.group(1)))
    return sorted(set(times))


def build_segments(duration, bounds):
    """Group scene boundaries into segments; insert forced cuts for long gaps."""
    cuts = [0.0]
    for b in bounds:
        if b - cuts[-1] >= MIN_SEG and b < duration - 20:
            cuts.append(b)
    refined = [cuts[0]]
    for c in cuts[1:]:
        prev = refined[-1]
        while c - prev > MAX_SEG:
            prev += FORCE_SEG
            refined.append(prev)
        refined.append(c)
    cuts = refined
    if duration - cuts[-1] > 20:
        cuts.append(duration)
    else:
        cuts[-1] = duration
    segs = list(zip(cuts, cuts[1:]))
    # Merge a tiny tail into the previous segment.
    if len(segs) > 1 and segs[-1][1] - segs[-1][0] < 20:
        segs[-2] = (segs[-2][0], segs[-1][1])
        segs.pop()
    return segs


def even_segments(duration, n=EVEN_CLIPS):
    step = duration / n
    return [(round(i * step, 1), round((i + 1) * step, 1)) for i in range(n)]


def main(video_path, out_path):
    duration = probe_duration(video_path)
    bounds = scene_boundaries(video_path)
    segments = build_segments(duration, bounds)
    method = "scene-detection"
    if len(segments) < MIN_CLIPS:
        segments = even_segments(duration)
        method = "even-splits-fallback"
    clips = []
    for i, (start, end) in enumerate(segments, 1):
        clips.append({
            "index": i,
            "start": round(start, 1),
            "end": round(end, 1),
            "duration": round(end - start, 1),
            "name": "clip-%02d_%04d-%04d.mp4" % (i, int(start), int(end)),
        })
    with open(out_path, "w") as f:
        json.dump({"method": method, "duration": round(duration, 1),
                   "scene_boundaries": len(bounds), "clips": clips}, f, indent=1)
    print("method=%s duration=%.1fs scene_boundaries=%d clips=%d"
          % (method, duration, len(bounds), len(clips)))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
