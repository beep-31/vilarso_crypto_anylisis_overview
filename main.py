import moviepy.editor as mp
import speech_recognition as sr
import dotenv
import os
import yt_dlp
import math
from openai import OpenAI
from pydub import AudioSegment

MP3_PATH = "audio/audio.mp3"
WAV_PATH = "audio/audio.wav"


dotenv.load_dotenv()


myOpenAI = OpenAI()
myOpenAI.api_key = os.getenv("OPENAI_API_KEY")

def download_audio(video_url, audio_filename = "audio/audio"):
    print("DOWNLOADING AUDIO")
    ydl_opts = {
        'format': 'bestaudio/best',  
        'outtmpl': audio_filename,   
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])


def chunk_audio(audio_path, chunck_length = 60000):
    audio = AudioSegment.from_wav(audio_path)
    chunks = []
    for i in range(0, len(audio), chunck_length):
        chunk = audio[i:i+chunck_length]
        chunk_name = f"audio/chunk_{i // chunck_length}.wav"
        chunk.export(chunk_name, format="wav")
        chunks.append(chunk_name)
    return chunks

def convert_mp3_to_wav(mp3_input = "audio/audio.mp3", wav_output = "audio/audio.wav"):
    print("CONVERTING TO WAV")
    audio = AudioSegment.from_mp3(mp3_input)
    audio.export(wav_output, format="wav")

def transcribe_audio_chunks(chunks):
    print("CREATING AUDIO TRANSCRIPTION")
    recognizer = sr.Recognizer()
    full_transcription = ""
    for chunk in chunks:
        print("Chunk ", chunk)
        with sr.AudioFile(chunk) as source:
            audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data, language="ru-RU") 
            full_transcription += text + " "
        except sr.UnknownValueError:
            print(f"Speech Recognition не смогло распознать chunk {chunk}")
    return full_transcription.strip()


def main():
    
    video_url = input("Paste the link to the video >>> ")
    audio_path = "audio/audio.wav"
    download_audio(video_url)
    convert_mp3_to_wav()
    chunks = chunk_audio(audio_path)
    text = transcribe_audio_chunks(chunks)
    print("SENDING THE REQUEST TO CHAT GPT")
    response = myOpenAI.chat.completions.create(
        model = "gpt-4o",
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Сделай мне отчет самого важного из этого текста и красиво его оформи чтобы он выглядел читабельно и так же напиши самые основные уровни сказанные автором:" + text}
        ]
    )
    print(response.choices[0].message.content)
    for chunk in chunks:
        os.remove(chunk)
    os.remove(MP3_PATH)
    os.remove(WAV_PATH)

main()


