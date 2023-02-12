import hashlib
from pytube import YouTube
import os

def download_audio(url):
    Downloaded_Audio_Path = os.path.abspath("youtube audio")

    print("\nStart downloading", url)
    yt = YouTube(url)

    hash_file = hashlib.md5()
    hash_file.update(yt.title.encode())

    file_name = Downloaded_Audio_Path +f'\\youtube.mp3'

    yt.streams.first().download("", file_name)
    print("Downloaded to", file_name)

    return {
        "file_name": file_name,
        "title": yt.title
    }

