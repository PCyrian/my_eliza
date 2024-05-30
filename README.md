# HUB: My_Eliza README

## Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Configuration](#configuration)
6. [Dependencies](#dependencies)

## Introduction

HUB: My_Eliza is an audio-based chatbot application that uses advanced language models and text-to-speech (TTS) systems to provide an interactive conversational experience. The application leverages customtkinter for the GUI, OpenAI's APIs for transcription and language model responses, and various TTS models for voice responses.

## Features

- **Audio Input and Transcription**: Record and transcribe audio input using OpenAI's Whisper API.
- **Language Model Interaction**: Interact with advanced language models such as GPT-3.5 Turbo and GPT-4o.
- **Text-to-Speech Synthesis**: Convert text responses to speech using local and cloud-based TTS models.
- **Local Voice Cloning**: Clone voices locally using provided speaker files for personalized TTS.
- **Customizable GUI**: Select STT, LLM, and TTS options via a user-friendly interface.
- **Settings Management**: Save and load user preferences for a personalized experience.
- **History Management**: Save and manage chat history for future reference.
- **Future Enhancements**: Upcoming integrations include additional STT options, local STT, News APIs, weather APIs, and calendar functionalities.

## Installation

### Prerequisites

- Ensure you have Python 3.8 or later installed. If not, the `installer.sh` script will guide you through the installation.

### Step-by-Step Installation

1. **Clone the Repository**:
    ```sh
    git clone https://github.com/PCyrian/my_eliza.git
    cd my_eliza
    ```

2. **Run the Installer Script**:
    The installer script will check and install Python (if necessary), and set up minimal libraries required for the wizard.
    ```sh
    chmod +x installer.sh
    ./installer.sh
    ```

3. **Run the Wizard**:
    The wizard will handle the installation of all dependencies and check for API keys, CUDA, and other requirements.
    ```sh
    python wizard.py
    ```

## Usage

1. **Start the Application**:
    ```sh
    python main.py
    ```

2. **Using the GUI**:
    - Select the desired Speech-to-Text (STT) service. Currently, only the Whisper API is available, but more options, including local ones, will be added soon.
    - Choose the Language Model (LLM) for generating responses.
    - Select the Text-to-Speech (TTS) option, including the local voice cloning feature.
    - Configure audio source and appearance settings.

3. **Interacting with the Chatbot**:
    - Use the "Speak" button to start and stop recording.
    - The chatbot will transcribe the audio, generate a response, and play the synthesized speech.
    - Chat history will be displayed in the GUI and saved for future sessions.

## Configuration

### GUI Settings

- **STT Options**: Whisper API (more options, including local STT, will be added soon).
- **LLM Options**: GPT-3.5 Turbo API, GPT-4o, local LLM (to be implemented).
- **TTS Options**: OpenAI TTS Nova, OpenAI TTS Alloy, Local TTS, Local Voice Cloning.
- **Appearance Modes**: System, Light, Dark.

### File Management

- **System Prompt**: Ensure `system_prompt.txt` is present in the root directory for initial system messages.
- **Chat History**: The chat history is stored in `chat_history.json`.
- **User Settings**: User settings are saved in `user_settings.json`.
- **Temporary Files**: Temporary audio files are stored and cleaned up automatically.

## Dependencies

- Python 3.8 or later
- customtkinter
- torch
- TTS
- pydub
- openai
- pygame
- other libraries handled by `wizard.py`

---

For any issues or questions, please open an issue on the [GitHub repository](https://github.com/yourusername/my_eliza/issues).
