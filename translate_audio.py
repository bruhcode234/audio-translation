import os
from pydub import AudioSegment
from gtts import gTTS
import subprocess
import re 
import time as time_module
from datetime import timedelta
import os 
import sys
from Create_Translated_SrtFile import CreateTranslatedSrt
import configparser
import platform
import winsound
import pyaudio
import wave

#---------------------------------------------------------------------------------------------------------------------------
def translate_audio(Pass,lang):
    os_name = platform.system()
    #get the link from setting.ini
    linkConfig = configparser.ConfigParser()
    linkConfig.read('setting.ini')
    link = str(linkConfig['SETTINGS']['link'])

    #get the speed limit from setting.ini
    speedConfig = configparser.ConfigParser()
    speedConfig.read('setting.ini')
    speed_limit = float(speedConfig['SETTINGS']['speed_limit'])
    
    #get the output path for the Audio Result and the translated SrtFile
    output_dir = os.path.abspath("Audio Output")
    srtFilepath = os.path.abspath("SrtFile")

    if lang == None:
        skip = 'n'
    else:
        skip = 'y'

    if skip == 'Y' or skip == 'y':
        lang_target = lang
        try:
            with open(srtFilepath + f"\\_SrtFile Path.srt","r") as f:
                srtFile = f.readlines()
                srtFile = srtFile[0].replace("\n","")
        except:
            print("You Still Haven't Created Any Srt File or there's no srt file path in _SrtFile Path.srt")
            sys.exit()
        print("\nPlease Make sure the srt file path is right in '_SrtFile Path.srt'")
        print("your translated srtFile : ",srtFile,"\n")    
        time_module.sleep(2)
        
    while True:
        if os.path.exists("raw_translated_1.mp3") == False:
            start = 0
            break

        try:
            start = int(input("where to start(int)? : "))
            if start == 0:
                start = start
            else:
                start = start - 1
            break
        except ValueError:
            print("that's not integer try again")

    #ASK 1
    while True:
        Continue = input("do you want to edit the text or the timestamp in translated srtFile if there's poor translated audio? (Y/N) : ")
        if Continue == 'Y' or Continue == 'y':
            decision = 'Y'
            break
        elif Continue == 'n' or Continue == 'N':
            file_name = str(input("\nenter your Audio Output file name you want to create : "))
            decision = 'N'
            break
        elif Continue != 'Y' and Continue != 'y':
            if Continue != 'n' and Continue != 'N':
                print("Invalid Answer, Try Again")

    if skip == 'N' or skip == 'n':
        if Pass == '1':
            Srt = CreateTranslatedSrt(link=link)
        elif Pass == '5':
            Srt = CreateTranslatedSrt(link=None)
        srtFile = Srt["Srt_File"]
        lang_target = Srt["lang_target"]
        print("your translated srtFile : ",srtFile,"\n")
    
    #Read the translated srtFile
    try:
        with open(srtFile,'r',encoding='utf-8') as f:
            lines = f.readlines()
    except:
        print("\nYou haven't create the srt file\n")
        sys.exit()
    time_stamp = 1
    text = 2
    Range = int(len(lines)/4)

    Bad_audio = []
    Speed_factor_list = []
    textX = []
    
    start_time_program = time_module.time()

    #Creating translated audio files
    for i in range(start,Range):    
        if i == start:
            print("Creating Required Audio Files")

            #Create Silent_1.mp3 if you haven't created any audio
            if i == 0:
                #Determine the first start_time to create Silent_0 file 
                time_complete = lines[time_stamp]
                time = time_complete.split('-->')
                start_time = time[0].split(':')
                start_time = start_time[2]
                start_time = float(re.sub(r'.', '', start_time, count = 1).replace(',','.'))

                #create the first silent audio or Silent_1.mp3 to add a pause before the first text is spoken
                silent = AudioSegment.silent(duration=start_time*1000, frame_rate=44100)
                silent.export("Silent_1.mp3", format="mp3")

            #in case you get an error and fail to run this program completely, you can choose where you want to start
            #if you choose 2 then the raw_translated creation process starts from 2 
            time_stamp = (start*4) + 1
            text = (start*4) + 2

        translated_text = lines[text]
        
        voice = gTTS(translated_text, slow=False, lang_check = True, lang=lang_target)        
        voice.save(f'raw_translated_{i+1}.mp3')                    
        
        #trim raw_translated audio to trim the silent in the last second of raw_translated_audio
        audio = AudioSegment.from_file(f'raw_translated_{i+1}.mp3')
        sus_sentence = lines[text]        
        
        #split the text 
        if sus_sentence[-1] == '?':
            sus_sentence = sus_sentence.split('?')
            sus_sentence = sus_sentence[-2]
        elif sus_sentence[-1] == '.':
            sus_sentence = sus_sentence.split('.')
            sus_sentence = sus_sentence[-2]
        elif sus_sentence[-1] == ',':
            sus_sentence = sus_sentence.split(',')
            sus_sentence = sus_sentence[-2]
        elif sus_sentence[-1] == '!':
            sus_sentence = sus_sentence.split('!')
            sus_sentence = sus_sentence[-2]

        for letter in sus_sentence:
            if ',' != letter:
                if letter == sus_sentence[-1]:
                    sus_sentence = sus_sentence[-1]
            else:
                sus_sentence = sus_sentence.split(',')
                sus_sentence = sus_sentence[-1]                

        #trim audio based on how many words the tts spoken after 200 characters
        if len(sus_sentence) > 200:                        
            sus_sentence = sus_sentence[200:]
            sus_sentence = sus_sentence.split()            
            if len(sus_sentence) == 3 or len(sus_sentence) < 3:
                audio = audio[:-300] #if 3, trim audio by 0.3 seconds from the end            
            elif len(sus_sentence) == 4:
                audio = audio[:-400] #if 4, trim audio by 0.4 seconds from the end            
            else:
                audio = audio[:-500] #if higher than above, trim 0.5
        #if the sentence doesn't reach 200 characters or more
        else:
            sus_sentence = sus_sentence.split()
            if len(sus_sentence) == 3 or len(sus_sentence) < 3:
                audio = audio[:-300] #if 3, trim audio by 0.3 seconds from the end            
            elif len(sus_sentence) == 4:
                audio = audio[:-400] #if 4, trim audio by 0.4 seconds from the end
            else:
                audio = audio[:-500] #if higher than above, trim 0.5            

        #change the index of lines[index] to get a next text
        text += 4        
        #export the trimmed audio
        audio.export(f'raw_translated_{i+1}.mp3')
        audio = AudioSegment.from_file(f'raw_translated_{i+1}.mp3')
        audio_duration = audio.duration_seconds

        #get the timestamp from the srtfile to get the desired duration
        time_complete = lines[time_stamp]
        time = time_complete.split('-->')
        start_time = time[0].split(':') 
        start_time_minutes = start_time[1]
        start_time = start_time[2]

        end_time = time[1].split(':')
        end_time_minutes = end_time[1]
        end_time = end_time[2]

        #get the start time minutes, remove 0 if the timestamp minute starts from unit number (0-9)
        start_time_minutes = float(start_time_minutes)

        #get the start time seconds, remove 0 if the timestamp second starts from unit number (0-9)
        start_time = float(start_time.replace(',','.'))
        start_time = start_time + (start_time_minutes * 60)
        
        #get the end time minutes, remove 0 if the timestamp minute starts from unit number (0-9)
        end_time_minutes = float(end_time_minutes)        

        #get the end time seconds, 0 if the timestamp second starts from unit number (0-9)
        end_time = float(end_time.replace(',','.').replace('\n',''))
        end_time = end_time + (end_time_minutes * 60)
                
        #get the desired duration and determine the audio speed
        desired_duration = end_time - start_time
        speed_factor = audio_duration/desired_duration
        command = f"sox raw_translated_{i+1}.mp3 translated_{i+1}.mp3 tempo {speed_factor}"
        subprocess.Popen(command,shell=True)
        
        while True:
            try:
                time_module.sleep(0.2)
                translated_duration = AudioSegment.from_file(f"translated_{i+1}.mp3",format="mp3")
                translated_duration = translated_duration.duration_seconds
                audio_diff = translated_duration - desired_duration
                break
            except:
                print("failed to get translated audio duration, trying to get it again...")

        #if the speed factor of a text is more than speed_limit it'll be considered as a bad audio
        #you have to shorten the translated text or extend the timestamp from the translated srt file to get a better audio
        if speed_factor > speed_limit and decision == 'Y' or decision == 'y':
            Bad_audio.append(int(i+1))
            Speed_factor_list.append(speed_factor)
            textX.append(lines[text-4])             

        #Create the silent audio from 2 to end, the timestamp must be more than 4 due to Index Error if time stamp < 4
        if time_stamp > 4:
            #get the end time of the timestamp before 
            time_complete_prior = lines[time_stamp-4]
            end_time_prior = time_complete_prior.split('-->')
            end_time_prior = end_time_prior[1].split(':')
            end_time_prior_minutes = end_time_prior[1]
            end_time_prior = end_time_prior[2]

            #get the time minutes of the previous time stamp
            end_time_prior_minutes = float(end_time_prior_minutes)

            #get the time seconds of the previous time stamp
            end_time_prior = float(end_time_prior.replace(',','.').replace('\n',''))
            end_time_prior = end_time_prior + (end_time_prior_minutes * 60)

            #get the desired duration silent. des_dur_sil = start time in time stamp now - end time in time stamp before
            desired_duration_silent = (start_time - end_time_prior) - float(audio_diff)
            
            #can't export the silent audio if the duration is lower than 0.0001
            if desired_duration_silent == 0 or desired_duration_silent < 0.0001:
                desired_duration_silent = 0.0001

            #Create the silent audio 
            silent = AudioSegment.silent(duration=(desired_duration_silent)*1000, frame_rate=44100)
            silent.export(f"Silent_{i+1}.mp3")

            # merging all the exported audio file into one file at the final iteration
            if i == Range-1:       
                print("100 %")            
                print("-"*50)

                #Shows how many audio that consired as poor audio
                print("total_poor_audio = ",len(Bad_audio))
                if len(Bad_audio) == 1:
                    print("there is 1 Bad translated audio file")
                    print("Bad translated audio is in number : ")
                    for j in range(len(Bad_audio)):
                        print("number : ",Bad_audio[j], "<-- speed = ", Speed_factor_list[j])
                        print("text : ",textX[j])
                    with open("_poor audio list.srt",'w',encoding='utf-8') as f:
                        f.write(str(Bad_audio[j]))

                elif len(Bad_audio) > 1:
                    print(f"there are {len(Bad_audio)} Bad translated audio files")
                    print("Bad translated audio files are in number : ")
                    for j in range(len(Bad_audio)):
                        print("\n","number : ",(Bad_audio[j]), "<-- speed = ", Speed_factor_list[j])
                        print("text : ",textX[j])       
                    with open("_poor audio list.srt",'w',encoding='utf-8') as f:
                        for k in range(len(Bad_audio)):
                            f.write(str(Bad_audio[k]))   
                            f.write("\n")  

                # if you choose 'Y' on ASK 3 (line 82), but there is no poor audio, it will continue the process                
                if Continue == 'y' or Continue == 'Y':
                    if len(Bad_audio) == 0:
                        file_name = srtFile.replace(os.path.abspath("SrtFile"),"").replace(".srt","").replace("\\","").replace(f"-{lang_target}","")
                        print("Exported to ",os.path.join(output_dir,file_name + f'-{lang_target}.mp3'))
                        decision ='n'
                    
                if decision == 'n' or decision == 'N':
                    #Merging silent and Translated audio
                    print("\nMerging Audio into one file")
                    for i in range(Range):
                        #get the audio using AudioSegment
                        translated_duration = AudioSegment.from_file(f"translated_{i+1}.mp3",format="mp3")
                        translated_duration = translated_duration.duration_seconds
                        Silent_duration = AudioSegment.from_file(f"Silent_{i+1}.mp3",format="mp3")
                        Silent_duration = Silent_duration.duration_seconds
                        if i == 0:
                            print(f"{int((i/Range)*100)}% complete")
                        if i > 0:
                            if i < 2:
                                #merging audio, starts from translated 1
                                Silent_audio = AudioSegment.from_file(f"Silent_{i+1}.mp3",format="mp3")
                                audio1 = AudioSegment.from_file(f"translated_{i}.mp3", format="mp3")
                                audio2 = AudioSegment.from_file(f"translated_{i+1}.mp3", format="mp3")
                                audio1 = audio1 + Silent_audio + audio2
                                print(f"{int((i/Range)*100)}% complete")
                            else:
                                Silent_audio = AudioSegment.from_file(f"Silent_{i+1}.mp3",format="mp3")
                                audio2 = AudioSegment.from_file(f"translated_{i+1}.mp3", format="mp3")
                                temp = audio1 + Silent_audio
                                audio1 = temp + audio2
                                print(f"{int((i/Range)*100)}% complete")                    

                        if i == Range-1:             
                            #merging the Silent_1.mp3 to the merged audio from the process before   
                            Silent_audio = AudioSegment.from_file(f"Silent_1.mp3",format="mp3")
                            audio1 = Silent_audio + audio1
                            audio1.export(os.path.join(output_dir,file_name + f'-{lang_target}.mp3'), format="mp3")
                            print(f"100% complete \n")
                            print("Merging Audio complete")                            
                            for i in range(Range):
                                if i == 0:
                                    print("Removing Unnecessary files")
                                os.remove(f"Silent_{i+1}.mp3")
                                os.remove(f"raw_translated_{i+1}.mp3")
                                os.remove(f"translated_{i+1}.mp3")
                                if i == Range-1:
                                    print("Removing Complete")
                                    end_time_program = time_module.time()
                                    total_time = end_time_program - start_time_program
                                    print("Total time for this program to run : ",str(timedelta(seconds=total_time)),"\n")
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
                    #Cancel merging audio process if you choose 'N' on ASK 3 (line 79)
                    print("Merging Audio Canceled\n")
                    print("run this program again after you edit the text or the timestamp\n")
                    print("note : if you add 1 second to the end_time of timestamp the speed will reduce by 0.25")
                    end_time_program = time_module.time()
                    total_time = end_time_program - start_time_program
                    if skip == 'n' or skip == 'N':
                        total_time = total_time + Srt["total_time"]
                        print("Total time for this program to run : ",str(timedelta(seconds=total_time)),"\n")
                        if os_name == "Windows":
                            winsound.PlaySound("notification.wav", winsound.SND_FILENAME)
                        else:
                            # Open the .wav file
                            wav_file = wave.open("notification.wav", "rb")
                            #
                            # Create a PyAudio object
                            p = pyaudio.PyAudio()
                            #
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
                    if skip == 'y' or skip == 'Y':
                        print("Total time for this program to run : ",str(timedelta(seconds=total_time)),"\n")
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

        print(f"{int(i/(Range-1)*100)} % ")
        time_stamp +=4
#---------------------------------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------------------------------
def fix_translated_audio():
    os_name = platform.system()
    #fix the translated audio if you want to edit the text or the timestamp in the srtFile
    print("\n_poor audio list.srt Detected")
    print("Fixing the translated audio file")
    speedConfig = configparser.ConfigParser()
    speedConfig.read('setting.ini')
    
    poor_audio_list = []    
    speed_list = []
    counter = 0
    #if the speed of the translated audio is too fast or higer than the speed limit, it will be put into this list
    bad_translated_audio = [] 
    file_name = str(input("\nEnter the name of the audio file you want to create : "))

    starting1 = time_module.time()
    
    #define the audio result path which is 'Audio Output' folder 
    #and 'SrtFile' folder for srtfile
    output_dir = os.path.abspath("Audio Output")
    srtFilepath = os.path.abspath("SrtFile")
    speed_limit = float(speedConfig['SETTINGS']['speed_limit'])
    
    #read the srtfile to get the poor audio file number
    with open("_poor audio list.srt",'r') as f:
        items = f.readlines()

    #get the srtfile path that you want to make the audio of it
    with open(srtFilepath + f"\\_SrtFile Path.srt",'r',encoding='utf-8') as f:
        srtFile = f.readlines()
        srtFile = srtFile[0].replace("\n","")
        lang_target = srtFile[-6:].replace('.srt','')

    #read the srtfile
    with open(srtFile,'r',encoding='utf-8') as f:
        lines = f.readlines()

    Range = int(len(lines)/4) #

    for item in items:
        negatif_index = False
        Index_Error = False    
        #get the text from srtfile
        changed_text = lines[(int(item) * 4) - 2]

        #This code retrieves the desired duration text currently in use
        #-------------------------------------------------------------------------------------------------
        time_complete = lines[(int(item) * 4) - 3]
        time = time_complete.split(" --> ")        
        current_start_time = time[0].split(':')
        current_end_time = time[1].split(':')        
        
        current_start_time_sec = float(current_start_time[2].replace(',','.'))
        current_start_time_min = float(current_start_time[1].replace(',','.'))
        current_end_time_sec = float(current_end_time[2].replace(',','.'))                    
        current_end_time_min = float(current_end_time[1].replace(',','.'))
        
        current_start_time = current_start_time_sec + (current_start_time_min * 60) #I
        current_end_time = current_end_time_sec + (current_end_time_min * 60) #II
        #desired duration text = #II - #I
        #-----------------------------------------------------------------------------------------------------
        
        #this code is to get desired duration Silent_x
        #-----------------------------------------------------------------------------------------------------                        
        time_complete = lines[((int(item) * 4) - 7)]
        time = time_complete.split(' --> ')        
        if ((int(item) * 4) - 7) <= 0:
            time_complete = lines[1]
            time = time_complete.split(' --> ')
            negatif_index = True
            previous_start_time = time[0].split(':')            
            previous_start_time_sec = float(previous_start_time[2].replace(',','.'))            
            previous_start_time_min = float(previous_start_time[1].replace(',','.'))            
            previous_start_time = previous_start_time_sec + (previous_start_time_min * 60) #VI            

        previous_end_time = time[1].split(':')        

        previous_end_time_sec = float(previous_end_time[2].replace(',','.'))
        previous_end_time_min = float(previous_end_time[1].replace(',','.'))

        previous_end_time = previous_end_time_sec + (previous_end_time_min * 60) #III                
        #desired duration silent x = #I - #III
        #-----------------------------------------------------------------------------------------------------

        #this code is to get desired duration Silent_x+1
        #-----------------------------------------------------------------------------------------------------
        try:
            time_complete = lines[((int(item) * 4) + 1)]
            time = time_complete.split(' --> ')

            next_start_time = time[0].split(':')
            next_end_time = time[1].split(':')

            next_start_time_sec = float(next_start_time[2].replace(',','.'))
            next_start_time_min = float(next_start_time[1].replace(',','.'))
            next_end_time_sec = float(next_end_time[2].replace(',','.'))
            next_end_time_min = float(next_end_time[1].replace(',','.'))

            next_start_time = next_start_time_sec + (next_start_time_min * 60) #IV
            next_end_time = next_end_time_sec + (next_end_time_min * 60) #V

        except IndexError:
            Index_Error = True
            print("Last Text Detected")
            pass

        #desired duration silent x+1 = #IV - #II
        #next desired duration text = #V - #IV
        #-----------------------------------------------------------------------------------------------------

        print(f"Creating new raw_translated_{int(item)}.mp3 in case the text changed")
        audio = gTTS(changed_text, lang=lang_target)
        audio.save(f"raw_translated_{int(item)}.mp3")

        audio = AudioSegment.from_file(f'raw_translated_{int(item)}.mp3')
        sus_sentence = changed_text

        #trim the raw translated audio
        if sus_sentence[-1] == '?':
            sus_sentence = sus_sentence.split('?')
            sus_sentence = sus_sentence[-2]
        elif sus_sentence[-1] == '.':
            sus_sentence = sus_sentence.split('.')
            sus_sentence = sus_sentence[-2]
        elif sus_sentence[-1] == ',':
            sus_sentence = sus_sentence.split(',')
            sus_sentence = sus_sentence[-2]
        elif sus_sentence[-1] == '!':
            sus_sentence = sus_sentence.split('!')
            sus_sentence = sus_sentence[-2]
                    
        for letter in sus_sentence:
            if ',' != letter:
                if letter == sus_sentence[-1]:
                    sus_sentence = sus_sentence
            else:
                sus_sentence = sus_sentence.split(',')
                sus_sentence = sus_sentence[-1]   

        #trim audio based on how many words it spokens after 200 characters
        if len(sus_sentence) > 200:
            sus_sentence = sus_sentence[200:]
            sus_sentence = sus_sentence.split()
            #if 3, trim audio by 0.3 seconds from the end
            if len(sus_sentence) == 3 or len(sus_sentence) < 3:
                audio = audio[:-300]
            #if 4, trim audio by 0.4 seconds from the end
            elif len(sus_sentence) == 4:
                audio = audio[:-400]
            #if higher than above, trim 0.5 from the end
            else:
                audio = audio[:-500]
        #if the characters doesn't reach 200 characters or higher, trim 0,5 from the end          
        else:
            sus_sentence = sus_sentence.split()
            if len(sus_sentence) == 3 or len(sus_sentence) < 3:
                audio = audio[:-300] #if 3, trim audio by 0.3 seconds from the end            
            elif len(sus_sentence) == 4:
                audio = audio[:-400] #if 4, trim audio by 0.4 seconds from the end
            else:
                audio = audio[:-500] #if higher than above, trim 0.5    

        #Create raw translated audio
        audio.export(f'raw_translated_{int(item)}.mp3')
        audio_duration = audio.duration_seconds

        #get desired_duration text
        desired_duration_text = current_end_time - current_start_time 
        if Index_Error != True:
            next_desired_duration_text = next_end_time - next_start_time

        #get the speed to change the duration
        speed_factor = audio_duration/desired_duration_text
        if speed_factor > speed_limit:
            bad_translated_audio.append(int(item))
        speed_list.append(speed_factor)
        poor_audio_list.append(int(item))
                
        print(f"Creating new translated_{int(item)}.mp3")
        command = f"sox raw_translated_{int(item)}.mp3 translated_{int(item)}.mp3 tempo {speed_factor}"
        subprocess.Popen(command,shell=True)

        #get the difference between the duration of translated.mp3 and desired_duration
        #---------------------------------------------------------------------------------------------------
        translated_duration = AudioSegment.from_file(f"translated_{int(item)}.mp3")
        translated_duration = translated_duration.duration_seconds
        audio_diff = translated_duration - desired_duration_text

        if Index_Error != True:
            next_translated_duration = AudioSegment.from_file(f"translated_{int(item) + 1}.mp3")
            next_translated_duration = next_translated_duration.duration_seconds
            next_audio_diff = next_translated_duration - next_desired_duration_text
        #-----------------------------------------------------------------------------------------------------

        #get desired silent duration and create silent audio
        #-----------------------------------------------------------------------------------------------------
        if negatif_index == True:            
            previous_desired_duration_silent = previous_start_time            
        else:
            previous_desired_duration_silent = current_start_time - previous_end_time - audio_diff    

        if previous_desired_duration_silent == 0 or previous_desired_duration_silent < 0.0001:
            previous_desired_duration_silent = 0.0001

        print(f"Creating new Silent_{int(item)}.mp3")
        silent = AudioSegment.silent(duration=(previous_desired_duration_silent)*1000, frame_rate=44100)
        silent.export(f"Silent_{int(item)}.mp3")
        time_module.sleep(0.3)    

        if Index_Error != True:
            next_desired_duration_silent = next_start_time - current_end_time - next_audio_diff
            if next_desired_duration_silent == 0 or next_desired_duration_silent < 0.0001:
                next_desired_duration_silent = 0.0001

            print(f"Creating new Silent_{int(item)+1}.mp3")
            silent = AudioSegment.silent(duration=(next_desired_duration_silent)*1000, frame_rate=44100)
            silent.export(f"Silent_{int(item)+1}.mp3")                
        #-------------------------------------------------------------------------------------------------------
        
        if item == items[-1]:            
            for i in poor_audio_list:
                print("\ntext num : ", i)
                print("speed : ", speed_list[counter])
                counter += 1     
            print(f"remove the audio num whose speed is lower than {speed_limit}  ")
            with open("_poor audio list.srt",'w',encoding='utf-8') as f:
                for num in bad_translated_audio:
                    f.write(str(num))
                    f.write("\n")

            while True:
                if os_name == "Windows":
                    winsound.PlaySound("notification.wav", winsound.SND_FILENAME)
                else:
                    # Open the .wav file
                    wav_file = wave.open("notification.wav", "rb")
                    #
                    # Create a PyAudio object
                    p = pyaudio.PyAudio()
                    #
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

                satisfy = input("Are you satisfied with the changes(Y) or No (N) : ")
                if satisfy == 'n' or satisfy == 'N':
                    sys.exit()
                elif satisfy == 'y' or satisfy == 'Y':
                    break
                else:
                    print("Invalid input, Try Again")
            break

    print("\nMerging Audio into one")

    for i in range(Range):
        translated_duration = AudioSegment.from_file(f"translated_{i+1}.mp3",format="mp3")
        translated_duration = translated_duration.duration_seconds
        Silent_duration = AudioSegment.from_file(f"Silent_{i+1}.mp3",format="mp3")
        Silent_duration = Silent_duration.duration_seconds
        if i == 0:
            print(f"{int((i/Range)*100)}% complete")
        if i > 0:
            if i < 2:
                Silent_audio = AudioSegment.from_file(f"Silent_{i+1}.mp3",format="mp3")
                audio1 = AudioSegment.from_file(f"translated_{i}.mp3", format="mp3")
                audio2 = AudioSegment.from_file(f"translated_{i+1}.mp3", format="mp3")
                audio1 = audio1 + Silent_audio + audio2
                print(f"{int((i/Range)*100)}% complete")
            else:
                Silent_audio = AudioSegment.from_file(f"Silent_{i+1}.mp3",format="mp3")
                audio2 = AudioSegment.from_file(f"translated_{i+1}.mp3", format="mp3")
                temp = audio1 + Silent_audio
                audio1 = temp + audio2
                print(f"{int((i/Range)*100)}% complete")    
                                
        if i == Range-1:
            Silent_audio = AudioSegment.from_file(f"Silent_1.mp3",format="mp3")
            audio1 = Silent_audio + audio1
            audio1.export(os.path.join(output_dir,file_name + f'-{lang_target}.mp3'), format="mp3")
            print(f"100% complete \n")
            print("Merging complete")
            for i in range(Range):
                if i == 0:
                    print("Removing Unnecessary files")
                os.remove(f"Silent_{i+1}.mp3")
                os.remove(f"raw_translated_{i+1}.mp3")
                os.remove(f"translated_{i+1}.mp3")
                if i == Range-1:
                    print("Removing Complete")
                    os.remove("_poor audio list.srt")
                                        
                    ending2 = time_module.time()
                    total_time1 = ending2 - starting1
                    print("Total time : ", str(timedelta(seconds=total_time1)))
                    if os_name == "Windows":
                            winsound.PlaySound("notification.wav", winsound.SND_FILENAME)
                    else:
                        # Open the .wav file
                        wav_file = wave.open("notification.wav", "rb")
                        #
                        # Create a PyAudio object
                        p = pyaudio.PyAudio()
                        #
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
#----------------------------------------------------------------------------------------------------------------------------


