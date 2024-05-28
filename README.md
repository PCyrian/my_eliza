Speech-to-Text with OpenAI GPT
This repository contains a Python-based application that utilizes OpenAI's API to transcribe speech to text, process the text with GPT, and respond with synthesized speech.

Requirements
Python 3.7+
pyaudio
wave
keyboard
pydub
pygame
mutagen
openai
ffmpeg
Installation
Clone the repository:

bash
Copy code
pip install pyaudio wave keyboard pydub pygame mutagen openai torch TTS
Ensure ffmpeg is installed and accessible in your PATH. You can download it from ffmpeg.org.

Setup
Set the OPENAI_API_KEY environment variable to your OpenAI API key:

bash
Copy code
export OPENAI_API_KEY='your-api-key-here'
Create a file named system_prompt.txt in the repository's root directory with the initial system prompt for the chatbot.

Usage
Run the application:

bash
Copy code
python main.py
Press and hold the SPACE key to start recording your voice. Release the SPACE key to stop recording.

The application will transcribe your speech, process it with GPT-3.5-turbo, and respond with synthesized speech.

Press the X key to exit the application.

File Structure
main.py: The main application code.
ffmpeg.exe: FFmpeg binary for audio processing.
system_prompt.txt: Initial system prompt for the chatbot.
chat_history.json: File where chat history is saved.
Notes
Ensure your microphone is correctly configured and accessible by the application.
The chat history is saved in chat_history.json and is loaded when the application starts.
Troubleshooting
If you encounter issues with recording, ensure your microphone index is correct. You can change the microphone_index parameter when initializing the AudioChatbot instance.
If transcription or speech synthesis fails, check your OpenAI API key and ensure it has the necessary permissions.