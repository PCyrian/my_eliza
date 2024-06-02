import os
import json
import customtkinter as ctk

stt_options = ["Whisper API", "Other TO BE IMPLEMENTED"]
llm_options = ["gpt3.5-turbo API", "gpt-4o", "Local LLM TO BE IMPLEMENTED"]
tts_options = ["OpenAI TTS nova", "OpenAI TTS alloy", "Local TTS", "Local voice cloning"]


def load_settings(selected_stt, selected_llm, selected_tts, selected_audio_source, appearance_mode):
    try:
        if os.path.exists("user_settings.json"):
            with open("user_settings.json", "r") as file:
                settings = json.load(file)
                selected_stt.set(settings.get("selected_stt", stt_options[0]))
                selected_llm.set(settings.get("selected_llm", llm_options[0]))
                selected_tts.set(settings.get("selected_tts", tts_options[0]))
                selected_audio_source.set(settings.get("selected_audio_source", ""))
                appearance_mode.set(settings.get("appearance_mode", "System"))
                ctk.set_appearance_mode(appearance_mode.get())
    except FileNotFoundError:
        pass


def save_settings(selected_stt, selected_llm, selected_tts, selected_audio_source, appearance_mode):
    settings = {
        "selected_stt": selected_stt.get(),
        "selected_llm": selected_llm.get(),
        "selected_tts": selected_tts.get(),
        "selected_audio_source": selected_audio_source.get(),
        "appearance_mode": appearance_mode.get(),
    }
    with open("user_settings.json", "w") as file:
        json.dump(settings, file)
