import tempfile
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
import torch
from TTS.api import TTS


device = "cuda" if torch.cuda.is_available() else "cpu"


def list_tts_models():
    print(TTS().list_models())


def generate_voice_line(text, speaker_file, output_file="output.wav"):
    tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts", progress_bar=True).to(device)
    tts.tts_to_file(text, speaker_wav=speaker_file, language="fr-fr", file_path=output_file)
    print(f"Audio saved to {output_file}")


def speak(text, output_file):
    speech_file_path = Path(__file__).parent / output_file
    speech_answer = openai.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text
    )
    speech_answer.stream_to_file(speech_file_path)


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


def convert_wav_to_mp3(wav_file, mp3_file):
    sound = AudioSegment.from_wav(wav_file)
    sound.export(mp3_file, format="mp3")
    os.remove(wav_file)


def generate_and_play_tts(text, speaker_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as wav_file:
        wav_file_path = wav_file.name
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as mp3_file:
        mp3_file_path = mp3_file.name

    try:
        generate_voice_line(text, speaker_file, wav_file_path)
        convert_wav_to_mp3(wav_file_path, mp3_file_path)
        play_mp3(mp3_file_path)
    finally:
        if os.path.exists(mp3_file_path):
            os.remove(mp3_file_path)


if __name__ == "__main__":
    test_text = "Hello, I am here to comfirm that not checking neither coding-style compliance or compilation of a new feature before comitting to main is indeed idiocratic at its finest. On a scale from 1 to 10, it's at least a 10"
    test2 = "Bonjour, ceci est un test de clonage audio du projet my_eliza"
    speaker_file_path = "voice_assets/speaker.wav"
    #generate_and_play_tts(test_text, speaker_file_path)
    generate_and_play_tts(test2, speaker_file_path)