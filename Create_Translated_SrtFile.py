import whisperx
from whisperx.utils import write_srt
import time
from googletrans import Translator
import os
from download import download_audio
import torch
from datetime import timedelta
import speech_recognition as sr
from subprocess import call
import wave
import numpy as np
import sys
translator = Translator()

def create_srt(file):
    device = "cpu"     
    if torch.cuda.is_available() == True:
        device == "cuda"
        fp = True
    else :
        fp = False

    output_dir = os.path.abspath("SrtFile")    
    file_name = input("Enter srt file name : ")
    print("Creating Your SrtFile...")
    model = whisperx.load_model('base')
    result = model.transcribe(audio=file,fp16 = fp)
    language_source_code = result['language'].replace(' ','')
    print("language source code : ",language_source_code)

    #check if the source language or language spoken in the video is the same as default language for alignment
    default_lang = ['en','fr','de','es','it','ja','zh','nl','uk','pt','ar','ru','pl','hu','fi','fa','el','tr']
    for language in default_lang:
        #if not then the text in result will be translated to 'en'  first then align it
        if language_source_code == language:
            print("Language Supported")
            break    
        elif language_source_code != language:
            if language == default_lang[-1]:                
                print("unsupported language detected, translate the transcribe result to 'en'")
                change_result = True                
                #create srt file with original whisper transcribe to double check the text
                print("Creating transcript text using speech recognition...")
                r = sr.Recognizer()
                #since speech recognizer can only transcribe wav audio file, we convert audio file extension to .wav first
                if file[-4:] != '.wav':
                    audio_suffix = file[-4:]
                    changed_audio_file_name = file.replace(file[-4:],'.wav')
                    if audio_suffix != ".wav":
                        call(["ffmpeg","-i",f"{file}",f"{changed_audio_file_name}"])

                with wave.open(changed_audio_file_name, "rb") as audio:
                    framerate = audio.getframerate()
                    n_frames = audio.getnframes()
                    duration = n_frames / framerate
                    audio_data = audio.readframes(n_frames)

                segment_duration = 60  # in seconds
                n_segments = int(np.ceil(duration / segment_duration))                

                segments = np.array_split(np.frombuffer(audio_data, dtype=np.int16), n_segments)                
                r = sr.Recognizer()
                with open(output_dir + f"/{file_name}.txt",'w',encoding='utf-8') as txt:
                    txt.write("The purpose of this file is to check is to check if the transcription is accurate\n")
                    for segment in segments:
                        audio = sr.AudioData(segment.tobytes(), framerate, sample_width=2)
                        transcribed_text = r.recognize_google(audio, language=language_source_code)                        
                        txt.write(transcribed_text)
                #translating the result text 
                result = translate_result(result=result) #we'll d                                             

    # align whisper output
    if change_result == False :        
        model_a, metadata = whisperx.load_align_model(language_code='en', device=device)
        result_aligned = whisperx.align(result["new_segments"], model_a, metadata, file, device)
        with open(os.path.join(output_dir, file_name + ".srt"), "w", encoding="utf-8") as srt:
            write_srt(result_aligned["segments"], file=srt)
    #if not supported
    else:
        with open(os.path.join(output_dir, file_name + ".srt"),'w', encoding='utf-8') as srt:
            write_srt(result["segments"],file=srt)    

def translate_result(result):
    translated_text_list = []

    for item in result["segments"]:
        translated = translator.translate(item['text'])
        translated_text_list.append(translated.text)
        if item == result["segments"][-1]:
            for i in range(len(result["segments"])):
                result["segments"][i]['text'] = translated_text_list[i]
    return{
        "new_segments":result["segments"]
    }

def translate_srt(srtfile,new_srtfile,target_lang):
    print("Creating your translated SrtFile...\n")

    output_dir = os.path.abspath("SrtFile")    

    with open(srtfile,'r',encoding='utf-8') as f:
        lines = f.readlines()

    Range = int(len(lines)/4)
    Id = 0
    TimeStamps = 1
    text = 2
    
    with open(new_srtfile,'w',encoding='utf-8') as transcript:
        print("Translated Text : ")
        for i in range(Range):
            translated = translator.translate(text= lines[text],src='auto', dest=target_lang)
            transcript.write(lines[Id])
            transcript.write(lines[TimeStamps])
            print(f"{i+1} : ",translated.text)
            transcript.write(str(translated.text))
            transcript.write("\n")
            transcript.write("\n")
            Id += 4
            TimeStamps += 4
            text += 4
            
            if text > len(lines):                
                break

    print("\nTranslated SrtFile Has Been Created\n")

    #Write srtfile path in '_SrtFile Path.srt'
    with open(output_dir + f"\\_SrtFile Path.srt","w",encoding='utf-8') as f:
        f.write(new_srtfile)
        f.write("\n")
        f.write(srtfile)


def CreateTranslatedSrt(link):
    program_start = time.time()
    translator = Translator()
    change_result = False 
    if link != None:
        audio_file = os.path.abspath("youtube audio") + f"\\youtube.mp3"
        file_name = input("Enter your Output SrtFile name : ")
    output_dir = os.path.abspath("SrtFile")
    
    while True:
        try:
            target_lang = input("enter target language code : ")
            text = "bread"
            translate_test = translator.translate(text=text,src='auto',dest=target_lang)
            break
        except ValueError:
            print("Invalid Target Language Code, Try Again.")

    if link != None:
        download_audio(link)
        print("audio has been downloaded\n")
    else:
        print("Create translated srt file with your audio")
        inp_audio_file = input("Enter your audio file name (with extension) : ")
        audio_file = os.path.abspath("your audio") + f"\\{inp_audio_file}"
        if os.path.exists(audio_file) != True :
            print("Can't Find The audio")
            sys.exit()
        file_name = input("Enter your Output SrtFile name : ")

    device = "cpu" 
    if torch.cuda.is_available() == True:
        device == "cuda"
        fp = True
    else :
        fp = False

    #change this to medium or large if you have high RAM --> RAM > 8
    whisper_model = "base"
    
    print("Creating SrtFile...")

    # transcribe with original whisper
    model = whisperx.load_model(whisper_model, device)
    result = model.transcribe(audio_file, fp16=fp)
        
    language_source_code = result['language'].replace(' ','')
    print("language source code : ",language_source_code)

    #check if the source language or language spoken in the video is the same as default language for alignment
    default_lang = ['en','fr','de','es','it','ja','zh','nl','uk','pt','ar','ru','pl','hu','fi','fa','el','tr']
    for language in default_lang:
        #if not then the text in result will be translated to 'en'  first then align it
        if language_source_code == language:
            print("Language is Supported")
            break    
        elif language_source_code != language:
            if language == default_lang[-1]:                
                print("unsupported language detected, translate the transcribe result to 'en'")
                change_result = True                
                #create srt file with original whisper transcribe to double check the text
                print("Creating transcript text using speech recognition...")
                r = sr.Recognizer()
                #since speech recognizer can only transcribe wav audio file, we convert audio file extension to .wav first
                if audio_file[-4:] != '.wav':
                    audio_suffix = audio_file[-4:]
                    changed_audio_file_name = audio_file.replace(audio_file[-4:],'.wav')
                    if audio_suffix != ".wav":
                        call(["ffmpeg","-i",f"{audio_file}",f"{changed_audio_file_name}"])

                with wave.open(changed_audio_file_name, "rb") as audio:
                    framerate = audio.getframerate()
                    n_frames = audio.getnframes()
                    duration = n_frames / framerate
                    audio_data = audio.readframes(n_frames)

                segment_duration = 60  # in seconds
                n_segments = int(np.ceil(duration / segment_duration))                

                segments = np.array_split(np.frombuffer(audio_data, dtype=np.int16), n_segments)                
                r = sr.Recognizer()
                with open(output_dir + f"/{file_name}.txt",'w',encoding='utf-8') as txt:
                    txt.write("The purpose of this file is to check is to check if the transcription is accurate\n")
                    for segment in segments:
                        audio = sr.AudioData(segment.tobytes(), framerate, sample_width=2)
                        transcribed_text = r.recognize_google(audio, language=language_source_code)                        
                        txt.write(transcribed_text)
                #translating the result text 
                result = translate_result(result=result) #we'll d

    print("Change_result = ",change_result)
    
    # align whisper result

    if change_result == False:
        time.sleep(1)
        model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
        result_aligned = whisperx.align(result["segments"], model_a, metadata, audio_file, device)        
    else :        
        time.sleep(1)
        model_a, metadata = whisperx.load_align_model(language_code='en', device=device)
        result_aligned = whisperx.align(result["new_segments"], model_a, metadata, audio_file, device)

    # create srt file using aligned whisper result
    with open(os.path.join(output_dir, file_name + " original.srt"), "w", encoding="utf-8") as srt:
        write_srt(result_aligned["segments"], file=srt)    

    print("\nSrtFile has been created")

    #create srt file path
    srtFile_old = os.path.join(output_dir, file_name + " original.srt")
    srtFile = os.path.join(output_dir, file_name + ".srt")
    srtFileName = srtFile.replace(".srt","")
    file_path = f"{srtFileName}-{target_lang}.srt"
    
    # Adjusting Timing and Sentences
    print("Adjusting the Sentences and Timestamps\n")
    with open(srtFile_old, 'r',encoding='utf-8') as f:
        lines = f.readlines()
    #remove the original.srt cause we don't need it anymore
    os.remove(srtFile_old)
    print(len(lines))

    srt_length = len(lines)
    TimeStamps = 1
    text = 2
    Range = int(len(lines)/4)
    end_last_timestamp = lines[srt_length-3]
    end_last_timestamp = end_last_timestamp.split(' --> ')

    #write srt file with time and text adjustment
    if target_lang == 'en' and change_result == True:
        srtFile = os.path.join(output_dir, file_name + f"-{target_lang}.srt")
        print("Exported to : ",srtFile)
    
    with open(srtFile,'w',encoding='utf-8') as f:
        for i in range(Range):
            lineWithText = lines[text].strip()
            lineWithTimeStampsNow = lines[TimeStamps]
            lineWithTimeStampsNow = lineWithTimeStampsNow.split(' --> ')

            current_end_time = lineWithTimeStampsNow[1].split(':')
            current_end_time = float(current_end_time[2].replace(',','.'))
            
            try:
                lineWithTimeStampsAfter = lines[TimeStamps + 4]
                lineWithTimeStampsAfter = lineWithTimeStampsAfter.split(' --> ')
                next_start_time = lineWithTimeStampsAfter[0].split(':')
                next_start_time = float(next_start_time[2].replace(',','.'))

                timestamp_diff = next_start_time - current_end_time
            except IndexError:
                pass            
                        
            while lineWithText[-1] != '.' and lineWithText[-1] != '!' and lineWithText[-1] != '?' and timestamp_diff < 0.3:
                text += 4
                TimeStamps += 4                
                if lineWithTimeStampsNow[1] == end_last_timestamp[1]:
                    TimeStamps = 1
                    text = 2
                    break
                lineWithText += ' ' + str(lines[text])
                lineWithText = lineWithText.replace('\n','')
                lineWithTimeStampsAfter = lines[TimeStamps]
                lineWithTimeStampsAfter = lineWithTimeStampsAfter.split(' --> ')
                lineWithTimeStampsNow[1] = lineWithTimeStampsNow[1].replace(lineWithTimeStampsNow[1],lineWithTimeStampsAfter[1])                

                if text+4 > len(lines):
                    break                
                if len(lineWithText) > 250:
                    break
            print(i+1)
            print(lineWithTimeStampsNow)            
            text += 4
            TimeStamps += 4
            print(lineWithText,'\n')
            f.write(f"{i+1}\n")
            f.write(lineWithTimeStampsNow[0] + ' --> ' + lineWithTimeStampsNow[1])
            f.write(lineWithText)
            f.write('\n')
            f.write('\n')            
            if lineWithTimeStampsNow[1] == end_last_timestamp[1]:
                TimeStamps = 1
                text = 2
                break
                        
    if target_lang == 'en' and change_result == True:
        with open(srtFile,'r',encoding='utf-8') as f:
            new_lines = f.readlines()
        new_TimeStamps = 1
        new_text = 2
        new_Range = int(len(new_lines)/4)
        srtFile = srtFile.replace(f"-{target_lang}","")
        print("Srt in Original Language is Exported to : ", srtFile)

        with open(srtFile,'w',encoding='utf-8') as transcript:
            for i in range(new_Range):
                transcript.write(f"{i+1}\n")
                transcript.write(str(new_lines[new_TimeStamps]))
                translated = translator.translate(text=new_lines[new_text],src='en',dest=language_source_code)
                transcript.write(str(translated.text))
                transcript.write("\n")
                transcript.write("\n")
                new_TimeStamps += 4
                new_text += 4             
        with open(output_dir + f"\\_SrtFile Path.srt",'w',encoding = 'utf-8') as f: 
            f.write(srtFile + f"-{target_lang}.srt\n") 
            f.write(srtFile)
    else:
        translate_srt(srtfile=srtFile,new_srtfile=file_path,target_lang=target_lang)
    
    program_end = time.time()
    program_total_time = program_end - program_start
    print("the amount of time it takes to create the srt file : ", str(timedelta(seconds= program_total_time)))
    return{
        "Srt_File": file_path,
        "total_time": program_total_time,
        "lang_target": target_lang,
    }
