# Description
This program allows you to translate the language of the speaker in an audio file to any language you want.

# How It Works
First, the program takes an audio file and transcribes it using WhisperX. Next, it creates a text-to-speech audio files (i named them raw_translated_x.mp3) using gTTS based on the transcription text and creates silence audio files using AudioSegment from pydub (i named them silence_x.mp3) to insert pauses in case the speaker stops talking for a while, then it changes the speed of raw_translated audio using sox to match the duration of the raw_translated audio with the duration in the transcription. the changed audio files will be saved as translated_x.mp3. Finally after creating all of silence audio and translated audio, it will merge all of them into a single audio file. 

# Setup
before you run this program, you have to download sox
##WILL FINISH THIS TOMMOROW
