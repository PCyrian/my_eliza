import pyaudio
import wave
import keyboard
from pydub import AudioSegment
import os
import openai
from pathlib import Path
import pygame
from mutagen.mp3 import MP3
import time

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 30
WAVE_OUTPUT_FILENAME = "temp.wav"
MP3_OUTPUT_FILENAME = "temp.mp3"
openai.api_key = "sk-proj-YgUozLpKOMYyT4nlpLNxT3BlbkFJplN2lP5GJVsy5BEffpyS"
MAX_HISTORY_LENGTH = 32


def play_mp3(file_path):
    pygame.init()
    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except pygame.error as e:
        print("Error playing MP3:", e)
    pygame.quit()


def convert_wav_to_mp3():
    sound = AudioSegment.from_wav(WAVE_OUTPUT_FILENAME)
    ffmpeg_path = "ffmpeg.exe"
    AudioSegment.converter = ffmpeg_path
    sound.export(MP3_OUTPUT_FILENAME, format="mp3")
    os.remove(WAVE_OUTPUT_FILENAME)


def record_audio(device_index):
    audio = pyaudio.PyAudio()

    input_device_params = {
        "format": FORMAT,
        "channels": CHANNELS,
        "rate": RATE,
        "input": True,
        "input_device_index": device_index,
        "frames_per_buffer": CHUNK
    }

    stream = audio.open(**input_device_params)

    frames = []

    while keyboard.is_pressed('space'):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))


def transcribe_audio(mp3_filename):
    try:
        with (open(mp3_filename, "rb") as audio_file):
            transcription = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            return transcription.text

    except Exception as e:
        print("Error:", e)
        return None


def chat_with_gpt(prompt):
    chat_history.append({"role": "user",
                         "content": prompt})
    API_response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=chat_history,
        temperature=1,
        max_tokens=363,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    chat_history.append({"role": "assistant",
                         "content": API_response.choices[0].message.content.strip()})
    return API_response.choices[0].message.content.strip()


def speak(text):
    speech_file_path = Path(__file__).parent / "speech.mp3"
    speech_answer = openai.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text
    )
    speech_answer.stream_to_file(speech_file_path)


def get_mp3_length(file_path):
    audio = MP3(file_path)
    return audio.info.length


def play_and_delete_mp3(file_path):
    play_mp3(file_path)
    time.sleep(get_mp3_length(file_path) + 1)
    os.remove(file_path)


if __name__ == "__main__":
    chat_history = [
            {
                "role": "system",
                "content": "You are Eliza. Part of the project \"My_ELIZA\" a reference to the first ever computer to process natural language. You are kind, smart and helpful. You will help in academic works and act as a friend. Try to me as concise and human-like as possible, avoid corporate talk or sounding like a dictionary by explaining things that are out of the question or expected to be known by the very premise of the question."
            }
        ]
    usb_microphone_index = 1
    while True:
        print(BLUE + "Press and hold SPACE to start recording..." + RESET)
        keyboard.wait('space')
        print(BLUE + "Recording..." + RESET)
        record_audio(usb_microphone_index)
        print(GREEN + "Recording complete. Audio saved as output.wav" + RESET)
        convert_wav_to_mp3()
        print(GREEN + "File converted from wav to mp3 successfully" + RESET)
        user_input = transcribe_audio(MP3_OUTPUT_FILENAME)
        print(GREEN + "Successfuly transcribed" + RESET)
        print(BLUE + "User speech transcription is ;" + RESET, user_input)
        response = chat_with_gpt(user_input)
        print(BLUE + "Chatbot ; " + response + RESET)
        speak(response)
        play_and_delete_mp3("speech.mp3")
        os.remove("temp.mp3")
        if len(chat_history) > MAX_HISTORY_LENGTH:
            chat_history = chat_history[-MAX_HISTORY_LENGTH:]
        if keyboard.is_pressed('x'):
            break
        else:
            pass
