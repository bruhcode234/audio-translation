import translate_audio
import os 
from Create_Translated_SrtFile import *
from googletrans import Translator  
import sys
import configparser
import platform
import winsound
import pyaudio 

linkConfig = configparser.ConfigParser()
linkConfig.read('setting.ini')
link = linkConfig['SETTINGS']['link']

if os.path.exists("raw_translated_1.mp3") == False or os.path.exists("_poor audio list.srt") == False:
    translator = Translator()
    os_name = platform.system()
    while True:        
        """ For option number 2, the program will take the srt file in the second line. 
                        option num 3 will take the first line"""
        print("-"*20,"AUDIO TRANSLATION PROGRAM","-"*20)
        print("1. Create srt file using the audio from youtube link in 'setting.ini'")  #can create translated audio file
        print("2. Create new srt file in '_SrtFile Path.srt' in new language") #can create translated audio file
        print("3. Create new translated audio file using the srt file in '_SrtFile Path.srt'") #it creates tl audio file     
        print("4. Just create srt file without translating or creating audio file using your audio file") #not create tl audio
        print("5. Create translated srt file using the audio from your audio folder") #can create translated audio file
        Option = input("Your choice (1 2 3 4 or 5) : ")
        if Option != '1' and Option != '2' and Option != '3' and Option != '4' and Option != '5':
            print("Invalid Choice, Try Again")
        elif Option == '1' or Option == '2' or Option == '5':
            while True:
                decision_1 = input("Do you want to create the audio too? (Y/N) : ")                
                if decision_1 != 'y' and decision_1 != 'Y' and decision_1 != 'n' and decision_1 != 'N':
                    print("Invalid Answer, Try Again")
                else:
                    break
            break
        else:
            break
    if Option == '1':        
        if decision_1 == 'n' or decision_1 == 'N':
            CreateTranslatedSrt(link=link)
            if os_name == "Windows":
                winsound.PlaySound("notification.wav", winsound.SND_FILENAME)            
            else:
                # Open the .wav file
                wav_file = wave.open("notification.wav", "rb")
                
                # Create a PyAudio object
                p = pyaudio.PyAudio()
                
                # Open a stream to play the .wav file
                stream = p.open(format=p.get_format_from_width(wav_file.getsampwidth()),
                                channels=wav_file.getnchannels(),
                                rate=wav_file.getframerate(),
                                output=True)
                # Read the data from the .wav file and play it
                data = wav_file.readframes(1024)
                while data:
                    stream.write(data)
                    data = wav_file.readframes(1024)
            sys.exit()
        else:
            translate_audio.translate_audio(Pass=Option,lang=None)
    elif Option == '2':
        while True:
            try:
                target_lang = input("Input new language code : ")
                text = "bread"
                translate_test = translator.translate(text=text,dest=target_lang)
                break
            except:
                print("Invalid language code, try again")

        with open(os.path.abspath("SrtFile") + f"\\_SrtFile Path.srt") as transcript:
            lines = transcript.readlines()

        srtfile1 = lines[1]
        temp = srtfile1.replace('.srt','')
        srtfile2 = temp + f"-{target_lang}.srt"
        print("\n")
        translate_srt(srtfile=srtfile1,new_srtfile=srtfile2,target_lang=target_lang)    
        if decision_1 == 'n' or decision_1 == 'N':
            sys.exit()    
        translate_audio.translate_audio(Pass= Option,lang = target_lang)
    elif Option == '3':
        with open(os.path.join(os.path.abspath("SrtFile") + f"\\_SrtFile Path.srt"),'r',encoding='utf-8') as f: 
            srt = f.readlines()
        srtfile = srt[0]
        lang = srtfile[-7:].replace('\n','').replace('.srt','')
        translate_audio.translate_audio(Pass = Option,lang=lang)    
    elif Option == '4':
        file_name = input("enter your audio file name (with extension) : ")
        audio_file = os.path.abspath("your audio") + f"\\{file_name}"
        create_srt(file=audio_file)
    elif Option == '5':
        if decision_1 == 'n' or decision_1 == 'N':
            CreateTranslatedSrt(link=None)
        elif decision_1 == 'y' or decision_1 == 'Y':
            translate_audio.translate_audio(Pass=Option, lang=None)
        
elif os.path.exists("_poor audio list.srt") == True :
    translate_audio.fix_translated_audio()
