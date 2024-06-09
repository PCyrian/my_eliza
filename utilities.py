import os
import threading

import pygame
from pydub import AudioSegment
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
from deep_translator import GoogleTranslator
import re
import logging

DetectorFactory.seed = 0


def save_wave_as_mp3(wav_filename, mp3_filename):
    sound = AudioSegment.from_wav(wav_filename)
    sound.export(mp3_filename, format="mp3")


def detect_language(transcription: str) -> str:
    try:
        language_code = detect(transcription)
        if language_code == "fr":
            return "fr"
        else:
            return "en"
    except LangDetectException:
        return "unknown"


def assure_language_continuity(chat_history: list[dict[str, str]], new_transcription: str) -> str:
    if len(chat_history) < 4:
        return new_transcription
    last_entry_content = chat_history[-1]["content"]
    last_language = detect_language(last_entry_content)
    new_language = detect_language(new_transcription)
    if new_language != last_language:
        translated = GoogleTranslator(source=new_language, target=last_language).translate(new_transcription)
        return translated
    return new_transcription

def split_text_into_sentences(text):
    logging.info(f"Original text: {text}\n")

    text = re.sub(r"[\"']", "", text)
    logging.info(f"Text after removing quotes: {text}\n")

    sentences = re.split(r'([.!?])', text)
    logging.info(f"Sentences after initial split: {sentences}\n")

    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if sentence in [".", "!", "?"]:
            current_chunk += sentence
            cleaned_chunk = current_chunk.strip()
            if re.search('[a-zA-Z]', cleaned_chunk):
                chunks.append(cleaned_chunk)
            current_chunk = ""
        else:
            current_chunk += sentence

    if current_chunk.strip() and re.search('[a-zA-Z]', current_chunk):
        chunks.append(current_chunk.strip())
        print(current_chunk + "\n")

    logging.info(f"Final text chunks: {chunks}")
    return chunks

def play_mp3(file_path):
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
