import pyaudio
import wave
import keyboard
from pydub import AudioSegment
import os
from openai import OpenAI

openai = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
from pathlib import Path
import pygame
from mutagen.mp3 import MP3
import time
import threading
from datetime import datetime
import json
import logging
from typing import List, Dict, Optional

# Configuration
WAVE_OUTPUT_FILENAME = "temp.wav"
MP3_OUTPUT_FILENAME = "temp.mp3"
if openai.api_key is None:
    raise ValueError("No API key set for OpenAI.")
MAX_HISTORY_LENGTH = 32

# Constants for terminal colors
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

# Audio Configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 30

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class AudioChatbot:
    def __init__(self, microphone_index: int, chat_history_file: str):
        self.microphone_index = microphone_index
        self.chat_history_file = chat_history_file
        self.chat_history = self.load_chat_history()
        if not self.chat_history:
            logging.info("No chat history found. Starting anew.")
            prompt_content = self.read_system_prompt()
            self.chat_history = [{"role": "system", "content": prompt_content}]
        else:
            logging.info("Chat history found.")

    def play_mp3(self, file_path: str) -> None:
        pygame.init()
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        except pygame.error as e:
            logging.error(f"Error playing MP3: {e}")
        finally:
            pygame.quit()

    def convert_wav_to_mp3(self, wav_filename: str, mp3_filename: str) -> None:
        sound = AudioSegment.from_wav(wav_filename)
        ffmpeg_path = "ffmpeg.exe"
        AudioSegment.converter = ffmpeg_path
        sound.export(mp3_filename, format="mp3")
        os.remove(wav_filename)

    def record_audio(self) -> None:
        audio = pyaudio.PyAudio()
        input_device_params = {
            "format": FORMAT,
            "channels": CHANNELS,
            "rate": RATE,
            "input": True,
            "input_device_index": self.microphone_index,
            "frames_per_buffer": CHUNK
        }

        stream = audio.open(**input_device_params)
        frames = []

        try:
            while keyboard.is_pressed('space'):
                data = stream.read(CHUNK)
                frames.append(data)
        finally:
            stream.stop_stream()
            stream.close()
            audio.terminate()

        with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))

    def transcribe_audio(self, mp3_filename: str) -> Optional[str]:
        try:
            with open(mp3_filename, "rb") as audio_file:
                transcription = openai.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
                return transcription.text
        except Exception as e:
            logging.error(f"Error transcribing audio: {e}")
            return None

    def chat_with_gpt(self, prompt: str) -> str:
        now = datetime.now()
        date_time_string = "Current Date, Day and Time:" + now.strftime("%Y-%m-%d %A %H:%M:%S")
        self.chat_history.append({"role": "user", "content": date_time_string + " / " + prompt})
        response = openai.chat.completions.create(model="gpt-3.5-turbo",
                                                  messages=self.chat_history,
                                                  temperature=1,
                                                  max_tokens=100,
                                                  top_p=1,
                                                  frequency_penalty=0,
                                                  presence_penalty=0)
        assistant_response = response.choices[0].message.content.strip()
        self.chat_history.append({"role": "assistant", "content": assistant_response})
        return assistant_response

    def speak(self, text: str) -> None:
        speech_file_path = Path(__file__).parent / "speech.mp3"
        try:
            speech_answer = openai.audio.speech.create(
                model="tts-1",
                voice="nova",
                input=text)
            speech_answer.stream_to_file(speech_file_path)
        except Exception as e:
            logging.error(f"Error creating speech: {e}")

    def get_mp3_length(self, file_path: str) -> float:
        audio = MP3(file_path)
        return audio.info.length

    def delayed_delete(self, file_path: str, delay: int) -> None:
        def task():
            time.sleep(delay)
            try:
                os.remove(file_path)
                logging.info(f"File {file_path} successfully deleted.")
            except Exception as e:
                logging.error(f"Failed to delete {file_path}: {e}")

        delete_thread = threading.Thread(target=task)
        delete_thread.start()

    def play_and_delete_mp3(self, file_path: str) -> None:
        self.play_mp3(file_path)
        self.delayed_delete(file_path, 10)  # Delete after 10 seconds

    def save_chat_history(self) -> None:
        try:
            with open(self.chat_history_file, 'w') as file:
                json.dump(self.chat_history, file, indent=4)
            logging.info("Chat history saved successfully.")
        except Exception as e:
            logging.error(f"Failed to save chat history: {e}")

    def load_chat_history(self) -> List[Dict[str, str]]:
        try:
            with open(self.chat_history_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            logging.warning("No existing chat history file found. Starting with an empty chat history.")
            return []
        except json.JSONDecodeError:
            logging.warning("Chat history file is empty or corrupted. Starting with an empty chat history.")
            return []

    def read_system_prompt(self) -> str:
        try:
            with open('system_prompt.txt', 'r') as file:
                content = file.read()
            return content
        except FileNotFoundError:
            return "The file 'system_prompt.txt' does not exist."
        except Exception as e:
            return f"An error occurred: {str(e)}"

    def handle_recording(self) -> Optional[str]:
        print(BLUE + "Press and hold SPACE to start recording..." + RESET)
        keyboard.wait('space')
        print(BLUE + "Recording..." + RESET)
        self.record_audio()
        print(GREEN + "Recording complete. Audio saved as output.wav" + RESET)
        self.convert_wav_to_mp3(WAVE_OUTPUT_FILENAME, MP3_OUTPUT_FILENAME)
        print(GREEN + "File converted from wav to mp3 successfully" + RESET)
        return self.transcribe_audio(MP3_OUTPUT_FILENAME)

    def process_transcription(self, user_input: str) -> str:
        print(GREEN + "Successfully transcribed" + RESET)
        print(BLUE + "User speech transcription is:" + RESET, user_input)
        self.save_chat_history()
        response = self.chat_with_gpt(user_input)
        print(BLUE + "Chatbot:" + response + RESET)
        return response

    def handle_response(self, response: str) -> None:
        self.speak(response)
        self.play_and_delete_mp3("speech.mp3")
        os.remove(MP3_OUTPUT_FILENAME)
        self.save_chat_history()

    def run(self) -> None:
        while True:
            user_input = self.handle_recording()
            if user_input:
                response = self.process_transcription(user_input)
                self.handle_response(response)
                if len(self.chat_history) > MAX_HISTORY_LENGTH:
                    self.chat_history = self.chat_history[-MAX_HISTORY_LENGTH:]
                if keyboard.is_pressed('x'):
                    break
            else:
                print(RED + "Failed to transcribe audio" + RESET)


if __name__ == "__main__":
    chatbot = AudioChatbot(microphone_index=1, chat_history_file='chat_history.json')
    chatbot.run()