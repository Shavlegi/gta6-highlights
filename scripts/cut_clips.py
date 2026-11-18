#!/usr/bin/env python3
"""Cut the clips listed in cutlist.json with ffmpeg stream copy (fast, no re-encode).

Usage: python3 cut_clips.py video.mp4 cutlist.json clips/
Writes clips/*.mp4 plus clips/manifest.txt (clip name, time range, duration).
"""
import json
import os
import subprocess
import sys


def main(video_path, cutlist_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    with open(cutlist_path) as f:
        data = json.load(f)
    lines = []
    for c in data["clips"]:
        out = os.path.join(out_dir, c["name"])
        subprocess.run(
            ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
             "-ss", str(c["start"]), "-to", str(c["end"]), "-i", video_path,
             "-c", "copy", "-avoid_negative_ts", "make_zero", out],
            check=True)
        lines.append("%s\t%.1f-%.1f\t%.1fs"
                     % (c["name"], c["start"], c["end"], c["duration"]))
    with open(os.path.join(out_dir, "manifest.txt"), "w") as f:
        f.write("method: %s\nvideo duration: %ss\nclips: %d\n\n"
                % (data["method"], data["duration"], len(data["clips"])))
        f.write("\n".join(lines) + "\n")
    print("cut %d clips -> %s" % (len(data["clips"]), out_dir))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
