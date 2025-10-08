#!/bin/bash

# Step 1: Ask the question out loud
echo "Asking the question: What is your zip code?"
pico2wave -w ask.wav "What is your zip code?" && aplay ask.wav

# Step 2: Record the user's response
echo "Recording your answer... Speak now!"
arecord -D plughw:2,0 -f cd -t wav -d 5 -r 16000 recorded_response.wav

# Step 3: Transcribe using whisper
echo "Transcribing your answer..."
python whisper_try.py recorded_response.wav

# Step 4: Let user know it’s done
echo "Done! Check the transcription above."
