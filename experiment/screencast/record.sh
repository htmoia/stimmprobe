#!/usr/bin/env bash
# Nimmt einen kurzen Vorführlauf des Experiments als Terminal-Screencast auf.
# Voraussetzung: asciinema und agg (brew install asciinema agg), laufender LLM-Server.
# Ergebnis: screencast/stimmprobe-experiment.cast, .gif und .mp4
set -euo pipefail
cd "$(dirname "$0")/.."

RUNS="${RUNS:-2}"
CONDITIONS="${CONDITIONS:-B C}"
OUT=screencast/stimmprobe-experiment

rm -f "$OUT.cast"
asciinema rec --window-size 120x36 --title "Stimmprobe: versteckte zweite Stimme gegen einen Pipecat-Agenten" \
  --command "../.venv/bin/python -W ignore run_experiment.py --runs $RUNS --conditions $CONDITIONS --out screencast/demo-results" \
  "$OUT.cast"

agg --font-size 15 --theme monokai --speed 1.5 "$OUT.cast" "$OUT.gif"
ffmpeg -y -loglevel error -i "$OUT.gif" -movflags faststart -pix_fmt yuv420p \
  -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" "$OUT.mp4"
ls -la screencast/
