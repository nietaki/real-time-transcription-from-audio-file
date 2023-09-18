#! /usr/bin/env bash

set -e

echo "$#"

if [ "$#" -lt 2 ] || [ "$#" -gt 2 ] || ! [ -f "$1" ]; then
  echo "Transcodes an audio/video file to be used with Assembly real-time transcription" >&2
  echo "" >&2
  echo "Usage:" >&2
  echo "$0 infile.mp4 outfile.wav" >&2
  exit 1
fi

sourcefile="$1"
destfile="$2"

ffmpeg -i "$sourcefile" -c:a pcm_s16le "$destfile"
