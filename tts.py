import torch
from pathlib import Path
from TTS.api import TTS
from utilities import save_wave_as_mp3
from pydub import AudioSegment
import os
import logging
import time
import openai
import threading

TTS_WAVE_OUTPUT_FILENAME = "temp_files/tts_output.wav"
TTS_MP3_OUTPUT_FILENAME = "temp_files/tts_output.mp3"

class TextToSpeech:
    def __init__(self):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.output = TTS_MP3_OUTPUT_FILENAME
        self.transcription_done_event = threading.Event()
        self.synthesis_done_event = threading.Event()

    def tts_local_female(self, text):
        tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=True).to(self.device)

        tts.tts_to_file(text=text, speaker_wav="voice_assets/speaker.wav", language="en", file_path=TTS_WAVE_OUTPUT_FILENAME)
        save_wave_as_mp3(TTS_WAVE_OUTPUT_FILENAME, TTS_MP3_OUTPUT_FILENAME)

    def tts_local_voice_cloning(self, text, speaker_file):
        if speaker_file is None:
            print("speaker_file is None")
            return None
        file_extension = speaker_file[-4:]
        print("file_extension : ", file_extension)
        print("speaker_file : ", speaker_file)
        if file_extension == ".mp3":
            audio = AudioSegment.from_mp3("input_file.mp3")
            audio.export("output_file.wav", format="wav")
            print("Conversion from MP3 to WAV completed successfully.")

        tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts", progress_bar=False).to(self.device)
        tts.tts_to_file(text, speaker_wav=speaker_file, language="en", file_path=TTS_WAVE_OUTPUT_FILENAME)
        save_wave_as_mp3(TTS_WAVE_OUTPUT_FILENAME, TTS_MP3_OUTPUT_FILENAME)

    def tts_openai(self, text, voice):
        speech_file_path = TTS_MP3_OUTPUT_FILENAME
        try:
            response = openai.audio.speech.create(
                model="tts-1",
                input=text,
                voice=voice
            )
            response.stream_to_file(speech_file_path)
            print(f"Speech synthesis successful, file saved at {speech_file_path}")
        except Exception as e:
            logging.error(f"Error creating speech: {e}")

    def tts_synthesis(self, text: str, tts_option: str, speaker_file: str):
        def run(text, tts_option, speaker_file):
            if tts_option == 'OpenAI TTS nova':
                self.tts_openai(text, 'nova')
            elif tts_option == 'OpenAI TTS alloy':
                self.tts_openai(text, 'alloy')
            elif tts_option == 'Local voice cloning':
                self.tts_local_voice_cloning(text, speaker_file)
            elif tts_option == 'Local TTS':
                self.tts_local_female(text)

        thread = threading.Thread(target=run, args=(text, tts_option, speaker_file))
        thread.start()
        thread.join()

