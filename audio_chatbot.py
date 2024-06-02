import os
import json
import threading
import time
import pygame
import logging
import openai
from datetime import datetime
from pathlib import Path
from typing import List, Dict
from audio import Audio
from tts import TextToSpeech
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
from utilities import save_wave_as_mp3, assure_language_continuity

DetectorFactory.seed = 0
SYSTEM_PROMPT_PATH = "data/system_prompt.txt"

class AudioChatbot:
    def __init__(self, microphone_index: int, chat_history_file: str, daily_report_file: str, add_message_to_gui,
                 selected_speaker_file):
        self.microphone_index = microphone_index
        self.chat_history_file = chat_history_file
        self.daily_report_file = daily_report_file
        self.chat_history = self.load_chat_history()
        self.chat_context = self.initialize_chat_context()
        self.audio = Audio()
        self.tts = TextToSpeech()
        self.add_message_to_gui = add_message_to_gui
        self.selected_llm = None
        self.selected_tts = None
        self.selected_speaker_file = selected_speaker_file
        self.transcription_done_event = threading.Event()
        self.synthesis_done_event = threading.Event()

    def initialize_chat_context(self):
        context = [
            {"role": "system", "content": self.read_system_prompt()},
            {"role": "system", "content": self.read_daily_report()}
        ]
        context.extend(self.chat_history)
        return context

    def read_system_prompt(self):
        try:
            with open(SYSTEM_PROMPT_PATH, "r") as file:
                return file.read().strip()
        except FileNotFoundError:
            logging.error("system_prompt.txt file not found.")
            return "You are a helpful assistant."

    def read_daily_report(self):
        try:
            with open(self.daily_report_file, "r", encoding="utf-8") as file:
                return file.read().strip()
        except FileNotFoundError:
            logging.error(f"{self.daily_report_file} not found.")
            return "Daily report not available."

    def load_chat_history(self):
        try:
            with open(self.chat_history_file, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            logging.warning("No existing chat history file found. Starting with an empty chat history.")
            return []

    def save_chat_history(self):
        with open(self.chat_history_file, "w") as file:
            json.dump(self.chat_history, file, indent=4)

    def print_chat_context(self):
        print("Current Chat Context:")
        for message in self.chat_context:
            print(f"{message['role']}: {message['content']}")

    def detect_language(self, transcription):
        try:
            return detect(transcription)
        except LangDetectException:
            return "unknown"

    def transcribe_audio(self):
        def run():
            try:
                self.audio.save_wave_as_mp3()
                with open(self.audio.output, "rb") as audio_file:
                    transcription = openai.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
                    self.transcription_result = assure_language_continuity(self.chat_history, transcription.text)
                self.transcription_done_event.set()
            except Exception as e:
                logging.error(f"Error transcribing audio: {e}")
                self.transcription_result = None
                self.transcription_done_event.set()

        self.transcription_done_event.clear()
        threading.Thread(target=run).start()
        self.transcription_done_event.wait()
        return self.transcription_result

    def play_mp3(self, file_path):
        if os.path.exists(file_path):
            def play_audio():
                pygame.init()
                try:
                    pygame.mixer.music.load(file_path)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        pygame.time.wait(100)
                finally:
                    pygame.mixer.quit()

            threading.Thread(target=play_audio).start()
        else:
            logging.error(f"File {file_path} not found.")

    def llm_gpt3_5_turbo(self, prompt):
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=self.chat_context,
            temperature=1,
            max_tokens=400,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response.choices[0].message.content.strip()

    def llm_gpt4o(self, prompt):
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=self.chat_context,
            temperature=1,
            max_tokens=400,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response.choices[0].message.content.strip()

    def chat_with_llm(self, prompt):
        now = datetime.now()
        date_time_string = "[SYSTEM INFO]Current Date, Day and Time:" + now.strftime("%Y-%m-%d %A %H:%M:%S")
        user_message = {"role": "user", "content": date_time_string + " / " + prompt}
        self.chat_history.append(user_message)
        self.chat_context.append(user_message)

        response_text = 'None'
        if self.selected_llm.get() == 'gpt3.5-turbo API':
            response_text = self.llm_gpt3_5_turbo(prompt)
        elif self.selected_llm.get() == 'gpt-4o':
            response_text = self.llm_gpt4o(prompt)
        if response_text == 'None':
            response_text = 'Chosen LLM was not found. Defaulting to gpt3.5-turbo API // ' + self.llm_gpt3_5_turbo(
                prompt)

        assistant_message = {"role": "assistant", "content": response_text}
        self.chat_history.append(assistant_message)
        self.chat_context.append(assistant_message)

        self.save_chat_history()
        return response_text

    def start_recording(self):
        self.audio.start_recording(self.microphone_index)
        threading.Thread(target=self.audio.record).start()

    def stop_recording(self):
        self.audio.stop_recording()
        self.start_audio_processing()

    def toggle_recording(self):
        if self.audio.stream is not None:
            self.stop_recording()
        else:
            self.start_recording()

    def process_audio(self):
        transcription = self.transcribe_audio()
        if transcription:
            print(f"Transcription: {transcription}")
            self.add_message_to_gui("You", transcription + '\n')
            response = self.chat_with_llm(transcription)
            print(f"LLM Response: {response}")
            self.add_message_to_gui("ELIZA", response + '\n')
            self.synthesis_done_event.clear()
            tts_thread = threading.Thread(target=self.tts_synthesis,
                                          args=(response, self.selected_tts.get(), self.selected_speaker_file.get()))
            tts_thread.start()
            tts_thread.join()
            self.play_mp3(self.tts.output)
        else:
            print("No transcription available.")
            self.add_message_to_gui("System", "No transcription available.\n")

    def start_audio_processing(self):
        processing_thread = threading.Thread(target=self.process_audio)
        processing_thread.start()

    def tts_synthesis(self, text, tts_option, speaker_file):
        if tts_option == 'OpenAI TTS nova':
            self.tts.tts_openai(text, 'nova')
        elif tts_option == 'OpenAI TTS alloy':
            self.tts.tts_openai(text, 'alloy')
        elif tts_option == 'Local voice cloning':
            self.tts.tts_local_voice_cloning(text, speaker_file)
        elif tts_option == 'Local TTS':
            self.tts.tts_local_female(text)
        self.synthesis_done_event.set()
