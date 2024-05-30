import torch
from pathlib import Path
from TTS.api import TTS
from utilities import save_wave_as_mp3
import logging
import openai

TTS_WAVE_OUTPUT_FILENAME = "temp_files/tts_output.wav"
TTS_MP3_OUTPUT_FILENAME = "temp_files/tts_output.mp3"

class TextToSpeech:
    def __init__(self):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.output = TTS_MP3_OUTPUT_FILENAME

    def tts_local_female(self, text):
        tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=True).to(self.device)
        tts.tts_to_file(text=text, file_path=TTS_WAVE_OUTPUT_FILENAME)
        save_wave_as_mp3(TTS_WAVE_OUTPUT_FILENAME, TTS_MP3_OUTPUT_FILENAME)

    def tts_openai(self, text, voice):
        speech_file_path = Path(__file__).parent / TTS_MP3_OUTPUT_FILENAME
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

    def tts_synthesis(self, text: str, tts_option: str):
        if tts_option == 'OpenAI TTS nova':
            self.tts_openai(text, 'nova')
        elif tts_option == 'OpenAI TTS alloy':
            self.tts_openai(text, 'alloy')
        elif tts_option == 'Local TTS':
            self.tts_local_female(text)
