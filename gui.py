import customtkinter as ctk
from settings import save_settings
import os
from tkinter import filedialog

stt_options = ["Whisper API", "Other TO BE IMPLEMENTED"]
llm_options = ["gpt3.5-turbo API", "gpt-4o", "Local LLM TO BE IMPLEMENTED"]
tts_options = ["OpenAI TTS nova", "OpenAI TTS alloy", "Local TTS", "Local voice cloning"]
appearance_modes = ["System", "Light", "Dark"]

class GUI:
    def __init__(self, root, audio_input_devices):
        self.root = root
        self.selected_stt = ctk.StringVar(value=stt_options[0])
        self.selected_llm = ctk.StringVar(value=llm_options[0])
        self.selected_tts = ctk.StringVar(value=tts_options[0])
        self.selected_speaker_file = ctk.StringVar(value="")
        self.selected_audio_source = ctk.StringVar(value="")
        self.appearance_mode = ctk.StringVar(value="System")
        self.chat_display = None
        self.file_button = None
        self.setup_gui(audio_input_devices)

    def setup_gui(self, audio_input_devices):
        stt_label = ctk.CTkLabel(self.root, text="Select STT:")
        stt_label.place(x=1050, y=50)
        stt_menu = ctk.CTkComboBox(self.root, variable=self.selected_stt, values=stt_options)
        stt_menu.place(x=1050, y=80)

        llm_label = ctk.CTkLabel(self.root, text="Select LLM:")
        llm_label.place(x=1050, y=120)
        llm_menu = ctk.CTkComboBox(self.root, variable=self.selected_llm, values=llm_options)
        llm_menu.place(x=1050, y=150)

        tts_label = ctk.CTkLabel(self.root, text="Select TTS:")
        tts_label.place(x=1050, y=190)
        tts_menu = ctk.CTkComboBox(self.root, variable=self.selected_tts, values=tts_options, command=self.update_tts_option)
        tts_menu.place(x=1050, y=220)

        appearance_label = ctk.CTkLabel(self.root, text="Theme:")
        appearance_label.place(x=1050, y=260)
        appearance_menu = ctk.CTkComboBox(self.root, variable=self.appearance_mode, values=appearance_modes, command=self.update_theme)
        appearance_menu.place(x=1050, y=290)

        audio_label = ctk.CTkLabel(self.root, text="Select Audio Source:")
        audio_label.place(x=1050, y=330)
        audio_menu = ctk.CTkComboBox(self.root, variable=self.selected_audio_source, values=audio_input_devices)
        audio_menu.place(x=1050, y=360)

        print_button = ctk.CTkButton(self.root, text="Print Selected Values", command=self.print_selected_values)
        print_button.place(x=1050, y=400)

        launch_button = ctk.CTkButton(self.root, text="Launch", command=self.print_selected_values)
        launch_button.place(x=1050, y=450)

        delete_button = ctk.CTkButton(self.root, text="Delete History", command=self.delete_history)
        delete_button.place(x=1050, y=500)

        self.chat_display = ctk.CTkTextbox(self.root, height=520, width=800, state=ctk.DISABLED)
        self.chat_display.place(relx=0.45, rely=0.4, anchor='center')

        quit_button = ctk.CTkButton(self.root, text="Quit", command=self.quit_app)
        quit_button.place(relx=0.08, rely=0.95, anchor='center')

        self.file_button = ctk.CTkButton(self.root, text="Select a speaker file", command=self.select_file)
        self.file_button.place(x=1050, y=550)
        self.file_button.place_forget()

    def update_tts_option(self, _=None):
        if self.selected_tts.get() == "Local voice cloning":
            self.file_button.place(x=1050, y=550)
        else:
            self.file_button.place_forget()

    def select_file(self):
        file_path = filedialog.askopenfilename(title="Select a speaker file", filetypes=[("Audio Files", "*.wav *.mp3")])
        if file_path:
            print(f"Selected file: {file_path}")
            self.selected_speaker_file.set(file_path)

    def print_selected_values(self):
        print(f"Selected STT: {self.selected_stt.get()}")
        print(f"Selected LLM: {self.selected_llm.get()}")
        print(f"Selected TTS: {self.selected_tts.get()}")
        print(f"Selected speaker_file: {self.selected_speaker_file.get()}")
        print(f"Selected Audio Source: {self.selected_audio_source.get()}")
        save_settings(self.selected_stt, self.selected_llm, self.selected_tts, self.selected_audio_source, self.appearance_mode)

    def delete_history(self):
        try:
            os.remove("./chat_history.json")
            print("History deleted successfully.")
        except FileNotFoundError:
            print("No history file found.")

    def update_theme(self, _=None):
        appearance = self.appearance_mode.get()
        ctk.set_appearance_mode(appearance)
        print(f"Appearance mode set to: {appearance}")
        save_settings(self.selected_stt, self.selected_llm, self.selected_tts, self.selected_audio_source, self.appearance_mode)

    def quit_app(self):
        save_settings(self.selected_stt, self.selected_llm, self.selected_tts, self.selected_audio_source, self.appearance_mode)
        temp_files = ["temp.wav", "tts_output.wav", "tts_output.mp3", "temp.mp3"]
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        self.root.quit()

    def add_message_to_gui(self, sender, message):
        self.chat_display.configure(state=ctk.NORMAL)
        self.chat_display.insert(ctk.END, f"{sender}: {message}\n")
        self.chat_display.configure(state=ctk.DISABLED)
