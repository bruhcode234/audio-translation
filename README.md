# Description
This program allows you to translate the language of the speaker in an audio file to any language you want.

# How It Works
1. the program takes an audio file and transcribe it using [WhisperX](https://github.com/m-bain/whisperX).
2. translates the transcription text into the language you want. 
3. creates a bunch of text-to-speech audio files (they will be saved as raw_translated_x.mp3) using [gTTS](https://github.com/pndurette/gTTS) based on the transcription text
4. creates a bunch of silent audio files using AudioSegment from [pydub](https://github.com/jiaaro/pydub) (they will be saved as silent_x.mp3) to insert pauses in case the speaker stops talking for a while.The silent audio duration is based on the difference between the start time of the current timestamp and the end time of the previous timestamp,
5. then it changes the speed of raw_translated audio using sox to match the duration of the raw_translated audio with the duration in the transcription. The changed audio files will be saved as translated_x.mp3. 
6. Finally after creating all of silent audio files and translated audio files, it will merge all of them into a single audio file which is the result of this program. and export it to Audio Output folder
7. Remove the raw_translated, translated, and silent audio files.
# Setup And Configuration
before you run this program, you have to install [SoX](https://sourceforge.net/projects/sox/) and install these [two files](https://app.box.com/s/tzn5ohyh90viedu3u90w2l2pmp2bl41t) and put it into SoX folder you installed so you won't get any error when running sox. next, you have to add the path of the sox folder you installed to the path in system variables from environment variables. after you've done all of that, you need install the requirements.

using pip :

```` pip -r install requirements.txt ````

then you need to enter a youtube video link in setting.ini if you want to translate a youtube audio. but if you want to translate your own audio file, put it into the 'your audio' folder and configure the speed limit of an audio that is also in setting.ini, the speed limit is used to determine poor audio, if the speed of translated audio is higher than the speed limit it'll be considered as a poor audio. The default speed limit is 1.8

# How To Use
simply run audio_translation.py on your IDE or cmd (i recommend you to run it on IDE). Once you run the script you will then be presented with several options along with some sub-options. These sub-options will ask you whether 
1. you want to create a translated audio output file and 
2. whether you want to edit the text or timestamps in the SRT file if there's poor translated audio. 

if you choose no 'n' on first sub option then it'll only creates srt file and if you choose yes 'y' on the second sub option, the program will print out the translated audio number that is considered as poor audio and the text it contains. you can shorten the translated text or extend the timestamps in the srt file. After you edit it you have to run the script again to continue the process. 

# For Unsupported Languages in WhisperX Alignment.
so whisperX alignment only supports a few languages, so there's chance the language of your audio file is not supported. The aligntment is used to get the accurate timestamps to write it on srt file. But don't worry i've solved it by translating the original whisper transcription text to english so you can use the whisperx alignment, but the text becomes incongruent with what the speaker says in the audio, therefore i use speech_recognition to transcribe your original audio file to text and save the result to txt file, to check if the transciption text is accurate. if you find a text that is inaccurate with what the speaker says in the srt file you can change it with the text in the txt file. yeah you'll need manual text transcribing if the language of your audio is not supported. After you finish checking and changing the text, you need to run the script again and choose option 2 (translate the srt file) to get a new and accurate translated srt file.


--some unimportant notes, i guess.

this repository is actually inspired by ThioJoe from the Auto-Synced-Translated-Dubs repository. i can't run the code in that repo cause Azure declined my card i don't know why 🤷‍♂️, so i decided to make the similiar program on my own. i'm sorry if the code kinda messy i'm still a noob at programming and github, Also i'm sorry if there's grammar mistake on this text and if you don't understand what i wrote, it's my second language.

for more details, here's a video on how to use this program.
