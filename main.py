import customtkinter as ctk
from settings import load_settings, save_settings
from gui import GUI
from audio_chatbot import AudioChatbot
from audio import Audio

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("HUB : My_Eliza")
root.geometry("1280x720")

audio = Audio()
audio_input_devices = audio.list_audio_input_devices()

gui = GUI(root, audio_input_devices)

chatbot = AudioChatbot(
    microphone_index=0,
    chat_history_file="chat_history.json",
    add_message_to_gui=gui.add_message_to_gui,
    selected_speaker_file=gui.selected_speaker_file
)

chatbot.selected_llm = gui.selected_llm
chatbot.selected_tts = gui.selected_tts

chatbot_toggle_button = ctk.CTkButton(root, text="Speak", command=chatbot.toggle_recording)
chatbot_toggle_button.place(x=1050, rely=0.85, anchor='center')

load_settings(gui.selected_stt, gui.selected_llm, gui.selected_tts, gui.selected_audio_source, gui.appearance_mode)

root.mainloop()
