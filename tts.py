import torch
from pathlib import Path
from TTS.api import TTS
from utilities import save_wave_as_mp3, detect_language, split_text_into_sentences, play_mp3
from pydub import AudioSegment
from pydub.playback import play
import os
import logging
import threading
import queue
import re
import openai
import time

TTS_WAVE_OUTPUT_FILENAME_TEMPLATE = "tts_output_{}.wav"
TTS_MP3_OUTPUT_FILENAME = "temp_files/tts_output.mp3"
SUPPORTED_LANGUAGES = ['en', 'fr']


class TextToSpeech:
    def __init__(self, temp_dir="temp_files/"):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.output = TTS_MP3_OUTPUT_FILENAME
        self.transcription_done_event = threading.Event()
        self.synthesis_done_event = threading.Event()
        self.temp_dir = temp_dir
        os.makedirs(self.temp_dir, exist_ok=True)
        print("using device:", self.device)

    def sanitize_text(self, text):
        return text.replace('"', '').strip()

    def concatenate_audio_files(self, filenames, output_filename):
        combined = AudioSegment.empty()
        for filename in filenames:
            audio = AudioSegment.from_wav(filename)
            combined += audio
        combined.export(output_filename, format="mp3")

    def play_audio_chunks(self, chunk_queue):
        while True:
            chunk_path = chunk_queue.get()
            if chunk_path is None:
                break
            audio = AudioSegment.from_file(chunk_path)
            play(audio)
            chunk_queue.task_done()

    def tts_local_female(self, text_chunks, chunk_queue):
        try:
            tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=True).to(self.device)

            for i, chunk in enumerate(text_chunks):
                logging.info(f"Processing chunk {i + 1}/{len(text_chunks)}: {chunk}")
                output_filename = os.path.join(self.temp_dir, TTS_WAVE_OUTPUT_FILENAME_TEMPLATE.format(i))
                language = detect_language(chunk)
                tts.tts_to_file(text=chunk, speaker_wav="ressources/voice_assets/speaker1.wav", language=language,
                                file_path=output_filename)
                chunk_queue.put(output_filename)

            chunk_queue.put(None)

        except Exception as e:
            logging.error(f"Error in tts_local_female: {e}")

    def tts_local_voice_cloning(self, text_chunks, speaker_file, chunk_queue):
        try:
            i = 0
            if speaker_file is None:
                logging.error("speaker_file is None")
                return

            if speaker_file.endswith(".mp3"):
                audio = AudioSegment.from_mp3(speaker_file)
                speaker_file = speaker_file.replace(".mp3", ".wav")
                audio.export(speaker_file, format="wav")

            tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts", progress_bar=False).to(self.device)

            for chunk in text_chunks:
                logging.info(f"Processing chunk: {chunk}")
                output_filename = os.path.join(self.temp_dir, TTS_WAVE_OUTPUT_FILENAME_TEMPLATE.format(i))
                language = detect_language(chunk)
                if language == "fr":
                    language = "fr-fr"
                tts.tts_to_file(text=chunk, speaker_wav=speaker_file, language=language, file_path=output_filename)
                chunk_queue.put(output_filename)
                i += 1

            chunk_queue.put(None)

        except Exception as e:
            logging.error(f"Error in tts_local_voice_cloning: {e}")

    def tts_openai(self, text, voice, chunk_queue):
        speech_file_path = TTS_MP3_OUTPUT_FILENAME
        try:
            response = openai.audio.speech.create(
                model="tts-1",
                input=text,
                voice=voice
            )
            response.stream_to_file(speech_file_path)
            chunk_queue.put(speech_file_path)
            chunk_queue.put(None)
            logging.info(f"Speech synthesis successful, file saved at {speech_file_path}")
        except Exception as e:
            logging.error(f"Error creating speech: {e}")

    def clean_files(self):
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        if os.path.exists(TTS_MP3_OUTPUT_FILENAME):
            os.remove(TTS_MP3_OUTPUT_FILENAME)

    def tts_synthesis(self, text: str, tts_option: str, speaker_file: str):
        self.clean_files()

        logging.info("Starting text synthesis")
        logging.info(f"Text to synthesize: {text}")
        logging.info(f"TTS option: {tts_option}")
        logging.info(f"Speaker file: {speaker_file}")
        logging.info(f"Raw text before splitting: {text}")
        text_chunks = split_text_into_sentences(text)
        logging.info(f"Text has been split into the following chunks: {text_chunks}")

        if text_chunks:
            logging.info("Text has been split into the following chunks:")
            for i, chunk in enumerate(text_chunks):
                logging.info(f"Chunk {i + 1}: {chunk}")

        chunk_queue = queue.Queue()

        def run(text_chunks, tts_option, speaker_file, chunk_queue):
            try:
                logging.info(f"Running TTS with text chunks: {text_chunks}")
                if tts_option == 'OpenAI TTS nova':
                    self.tts_openai(' '.join(text_chunks), 'nova', chunk_queue)
                elif tts_option == 'OpenAI TTS alloy':
                    self.tts_openai(' '.join(text_chunks), 'alloy', chunk_queue)
                elif tts_option == 'Local voice cloning':
                    self.tts_local_voice_cloning(text_chunks, speaker_file, chunk_queue)
                elif tts_option == 'Local TTS':
                    self.tts_local_female(text_chunks, chunk_queue)
            except Exception as e:
                logging.error(f"Error in run method: {e}")

        processing_thread = threading.Thread(target=run, args=(text_chunks, tts_option, speaker_file, chunk_queue))
        playback_thread = threading.Thread(target=self.play_audio_chunks, args=(chunk_queue,))

        processing_thread.start()
        playback_thread.start()

        processing_thread.join()
        playback_thread.join()


logging.basicConfig(level=logging.INFO)
