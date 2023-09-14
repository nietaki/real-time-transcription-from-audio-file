#!/usr/bin/env bash

rtx install python
rtx use python
pip install wave
pip install pyaudio
pip install websockets

cp -n configure.py.example configure.py
ffmpeg -i sample_files/Backend_Sync_ee9209cd-6cd2-4271-b745-3e10384ae202.mp4 -c:a pcm_s16le sample_files/output.wav
