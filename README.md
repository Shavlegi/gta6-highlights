# YouTube highlight clips — GTA 6 Prologue & First Mission

Source video: https://youtu.be/kQeywW8-w20
("GTA 6 Prologue & First Mission FULL GAMEPLAY (Lucia & Jason)", 40:24,
uploader "Formula". The video has no chapters, so cuts are found automatically.)

## What this repo does

A GitHub Actions workflow downloads the video with yt-dlp, finds highlight
boundaries with ffmpeg scene detection, cuts 20+ clips (~75–150 s each) with
ffmpeg stream copy, and uploads them as a workflow artifact plus a GitHub
Release. Nothing is published to Instagram or anywhere else — cutting only.

If scene detection finds too few cuts, the script falls back to 24 even splits
and says so in `manifest.txt`.

## How to run it

The workflow runs automatically on push. When it finishes, download the
clips from **Actions → Cut highlight clips → Artifacts → gta6-highlights**,
or from the **Releases** page. Public repos get free Actions minutes.

To re-run with no changes: Actions → Cut highlight clips → Run workflow.

## Files

- `.github/workflows/cut-highlights.yml` — the Actions workflow
- `scripts/make_cutlist.py` — scene detection + cut-list builder (with
  even-split fallback)
- `scripts/cut_clips.py` — ffmpeg cutting + manifest writer
