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

class AudioChatbot:
    def __init__(self, microphone_index: int, chat_history_file: str, daily_report_file: str, add_message_to_gui, selected_speaker_file):
        self.microphone_index = microphone_index
        self.chat_history_file = chat_history_file
        self.daily_report_file = daily_report_file
        self.chat_history = self.load_chat_history()
        if not self.chat_history:
            logging.info("No chat history found. Starting anew.")
            prompt_content = self.read_system_prompt()
            self.chat_history = [{"role": "system", "content": prompt_content}]
        else:
            logging.info("Chat history found.")
        self.audio = Audio()
        self.tts = TextToSpeech()
        self.add_message_to_gui = add_message_to_gui
        self.selected_llm = None
        self.selected_tts = None
        self.selected_speaker_file = selected_speaker_file
        self.import_daily_report()
        self.transcription_done_event = threading.Event()
        self.synthesis_done_event = threading.Event()

    def import_daily_report(self):
        file_path = self.daily_report_file
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                self.chat_history.append({"role": "system", "content": "The following is an automated daily report\n" + content})
            return content
        except Exception as e:
            print(f"Error reading file: {e}")
            return None

    def play_mp3(self, file_path: str) -> None:
        def play_audio():
            pygame.init()
            try:
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
            finally:
                pygame.mixer.quit()

        threading.Thread(target=play_audio).start()

    def read_system_prompt(self) -> str:
        try:
            with open("system_prompt.txt", "r") as file:
                return file.read().strip()
        except FileNotFoundError:
            logging.error("system_prompt.txt file not found.")
            return "You are a helpful assistant."

    def load_chat_history(self) -> List[Dict[str, str]]:
        try:
            with open(self.chat_history_file, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            logging.warning("No existing chat history file found. Starting with an empty chat history.")
            return []

    def save_chat_history(self) -> None:
        with open(self.chat_history_file, "w") as file:
            json.dump(self.chat_history, file, indent=4)

    def detect_language(self, transcription: str) -> str:
        try:
            language_code = detect(transcription)
            return language_code
        except LangDetectException:
            return "unknown"

    def transcribe_audio(self) -> str:
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
        thread = threading.Thread(target=run)
        thread.start()
        self.transcription_done_event.wait()
        return self.transcription_result

    def llm_gpt3_5_turbo(self, prompt: str):
        response = openai.chat.completions.create(model="gpt-3.5-turbo",
                                                  messages=self.chat_history,
                                                  temperature=1,
                                                  max_tokens=400,
                                                  top_p=1,
                                                  frequency_penalty=0,
                                                  presence_penalty=0)
        response_text = response.choices[0].message.content.strip()
        return response_text

    def llm_gpt4o(self, prompt: str):
        response = openai.chat.completions.create(model="gpt-4o",
                                                  messages=self.chat_history,
                                                  temperature=1,
                                                  max_tokens=400,
                                                  top_p=1,
                                                  frequency_penalty=0,
                                                  presence_penalty=0)
        response_text = response.choices[0].message.content.strip()
        return response_text

    def chat_with_llm(self, prompt: str) -> str:
        now = datetime.now()
        date_time_string = "[SYSTEM INFO]Current Date, Day and Time:" + now.strftime("%Y-%m-%d %A %H:%M:%S")
        self.chat_history.append({"role": "user", "content": date_time_string + " / " + prompt})
        response_text = 'None'
        if self.selected_llm.get() == 'gpt3.5-turbo API':
            response_text = self.llm_gpt3_5_turbo(prompt)
        elif self.selected_llm.get() == 'gpt-4o':
            response_text = self.llm_gpt4o(prompt)
        if response_text == 'None':
            response_text = 'Chosen LLM was not found. Defaulting to gpt3.5-turbo API // '
            response_text += self.llm_gpt3_5_turbo(prompt)
        self.chat_history.append({"role": "assistant", "content": response_text})
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

    def process_audio(self) -> None:
        transcription = self.transcribe_audio()
        if transcription:
            print(f"Transcription: {transcription}")
            self.add_message_to_gui("You", transcription + '\n')

            response = self.chat_with_llm(transcription)
            print(f"LLM Response: {response}")
            self.add_message_to_gui("ELIZA", response + '\n')

            self.synthesis_done_event.clear()
            tts_thread = threading.Thread(target=self.tts_synthesis, args=(response, self.selected_tts.get(), self.selected_speaker_file.get()))
            tts_thread.start()
            tts_thread.join()
            self.play_mp3(self.tts.output)
        else:
            print("No transcription available.")
            self.add_message_to_gui("System", "No transcription available.\n")

    def start_audio_processing(self):
        processing_thread = threading.Thread(target=self.process_audio)
        processing_thread.start()

    def tts_synthesis(self, text: str, tts_option: str, speaker_file: str):
        if tts_option == 'OpenAI TTS nova':
            self.tts.tts_openai(text, 'nova')
        elif tts_option == 'OpenAI TTS alloy':
            self.tts.tts_openai(text, 'alloy')
        elif tts_option == 'Local voice cloning':
            self.tts.tts_local_voice_cloning(text, speaker_file)
        elif tts_option == 'Local TTS':
            self.tts.tts_local_female(text)
        self.synthesis_done_event.set()

