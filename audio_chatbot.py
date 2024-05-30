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

class AudioChatbot:
    def __init__(self, microphone_index: int, chat_history_file: str, add_message_to_gui, selected_speaker_file):
        self.microphone_index = microphone_index
        self.chat_history_file = chat_history_file
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

    def transcribe_audio(self) -> str:
        try:
            self.audio.save_wave_as_mp3()
            with open(self.audio.output, "rb") as audio_file:
                transcription = openai.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
                return transcription.text
        except Exception as e:
            logging.error(f"Error transcribing audio: {e}")
            return None

    def llm_gpt3_5_turbo(self, prompt: str):
        response = openai.chat.completions.create(model="gpt-3.5-turbo",
                                                  messages=self.chat_history,
                                                  temperature=1,
                                                  max_tokens=100,
                                                  top_p=1,
                                                  frequency_penalty=0,
                                                  presence_penalty=0)
        response_text = response.choices[0].message.content.strip()
        return response_text

    def llm_gpt4o(self, prompt: str):
        response = openai.chat.completions.create(model="gpt-4o",
                                                  messages=self.chat_history,
                                                  temperature=1,
                                                  max_tokens=100,
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
        self.process_audio()

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
            self.add_message_to_gui("my_Eliza", response + '\n')

            self.tts.tts_synthesis(response, self.selected_tts.get(), self.selected_speaker_file.get())
            self.play_mp3(self.tts.output)
        else:
            print("No transcription available.")
            self.add_message_to_gui("System", "No transcription available.\n")
