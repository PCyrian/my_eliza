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
import threading
from datetime import datetime
import json

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
openai.api_key = os.getenv('OPENAI_API_KEY')
if openai.api_key is None:
    raise ValueError("No API key set for OpenAI.")
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
    now = datetime.now()
    date_time_string = "Current Date, Day and Time:" + now.strftime("%Y-%m-%d %A %H:%M:%S")
    chat_history.append({"role": "user",
                         "content": date_time_string + " / " + prompt})
    API_response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=chat_history,
        temperature=1,
        max_tokens=100,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    chat_history.append({
                         "role": "assistant",
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


def delayed_delete(file_path, delay):
    def task():
        time.sleep(delay)
        try:
            os.remove(file_path)
            print(f"File {file_path} successfully deleted.")
        except Exception as e:
            print(f"Failed to delete {file_path}: {e}")

    delete_thread = threading.Thread(target=task)
    delete_thread.start()


def play_and_delete_mp3(file_path):
    play_mp3(file_path)


def save_chat_history(history, filename):
    try:
        with open(filename, 'w') as file:
            json.dump(history, file, indent=4)
        print("Chat history saved successfully.")
    except Exception as e:
        print(f"Failed to save chat history: {e}")


def load_chat_history(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print("No existing chat history file found. Starting with an empty chat history.")
        return []
    except json.JSONDecodeError:
        print("Chat history file is empty or corrupted. Starting with an empty chat history.")
        return []

def read_system_prompt():
    try:
        with open('system_prompt.txt', 'r') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return "The file 'system_prompt.txt' does not exist."
    except Exception as e:
        return f"An error occurred: {str(e)}"


if __name__ == "__main__":
    chat_history = load_chat_history('chat_history.json')
    if not chat_history:
        print("No chat history found. Starting anew.")
        prompt_content = read_system_prompt()
        chat_history = [
                {
                    "role": "system",
                    "content": prompt_content
                }
            ]
    else:
        print("Chat history found.")
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
        save_chat_history(chat_history, 'chat_history.json')
        response = chat_with_gpt(user_input)
        print(BLUE + "Chatbot ; " + response + RESET)
        speak(response)
        play_and_delete_mp3("speech.mp3")
        os.remove("temp.mp3")
        os.remove("speech.mp3")
        save_chat_history(chat_history, 'chat_history.json')
        if len(chat_history) > MAX_HISTORY_LENGTH:
            chat_history = chat_history[-MAX_HISTORY_LENGTH:]
        if keyboard.is_pressed('x'):
            break
        else:
            pass
