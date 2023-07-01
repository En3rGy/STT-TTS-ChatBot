import sys
import time
import json
import wave
import logging
from typing import List, Dict
import configparser
import os

import pyaudio


SAMPLE_RATE = 16000
# CHUNK_SIZE = 2048
CHUNK_SIZE = 1024
AUDIO_FORMAT = pyaudio.paInt16
TIMEOUT = 15

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def play_wav(filename, device_index=None):
    """
    @brief Plays a WAV audio file using the PyAudio library.

    @param filename: The path to the WAV file that should be played.
    """
    chunk = 1024


    logger.info("Opening file")
    wf = wave.open(filename, 'rb')

    logger.info("Creating pyaudio")
    p = pyaudio.PyAudio()

    device_info = p.get_device_info_by_index(device_index) if device_index else None

    logger.info("Opening stream")
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True,
                    output_device_index=device_info["index"] if device_info else None)

    data = wf.readframes(chunk)
    while data:
        stream.write(data)
        data = wf.readframes(chunk)

    logger.info("Close stream")
    stream.close()
    p.terminate()


def main() -> None:
    """
    @brief Main function to run the voice-activated chatbot using the Vosk and OpenAI APIs.

    Sets up the necessary components, such as the KaldiRecognizer, PyAudio, and the TTS engine.
    Listens for the trigger phrase, then transcribes speech and generates responses using the OpenAI API.
    Return to wait for the trigger phrase, listening and responding until the termination phrase is detected.
    """

    logger.info("Start...")
    sound_file = "./audio.wav"
    play_wav(sound_file, 0)

    sound_file = "./recording.wav"
    play_wav(sound_file, 0)



if __name__ == "__main__":
    logger.info(f"{__file__}:{__name__}")
    main()
