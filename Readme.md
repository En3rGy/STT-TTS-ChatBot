# Voice-Activated Chatbot

This repository contains a voice-activated chatbot that utilizes the Vosk and OpenAI APIs to recognize speech, transcribe audio, and generate responses using a pre-trained language model.

## Features

- Listens for a trigger phrase to start processing user input
- Transcribes user speech using the Vosk speech recognition library
- Generates responses to user questions or statements using the OpenAI API
- Uses the pyttsx3 library for text-to-speech output
- Continues listening and responding until a termination phrase is detected

## Dependencies

- [vosk](https://pypi.org/project/vosk/)
- [pyaudio](https://pypi.org/project/PyAudio/)
  - `sudo apt-get install portaudio19-dev python3-pyaudio`
- [pyttsx3](https://pypi.org/project/pyttsx3/)
  - `sudo apt-get install espeak`
- [openai](https://pypi.org/project/openai/)

## Installation

1. Clone this repository
2. Install the required dependencies:<br>`pip install vosk pyaudio pyttsx3 openai`
3. Create a credentials file at `./etc/credentials.txt` and add your open ai API key to <br>`{"openai_api": OPEN_AI_API_KEY}`.
4. Store the voks [model](https://alphacephei.com/vosk/models) at `./etc/models` and set the path as value of `MODEL_PATH` in stt.py
5. Check the constants in stt.py

## Usage

Run the main script: `python main.py`

The chatbot will listen for the trigger phrase (e.g., "Hey, computer") before processing user input. It will continue listening and responding until the termination phrase (e.g., "Ende") is detected.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
