import sys
import os
import time
import json
import wave
import logging
from typing import List, Dict

import pyaudio
import pyttsx4
import openai
from vosk import Model, KaldiRecognizer


# Constants
TRIGGER_PHRASE = "hey computer"
QUIT_TRIGGER_PHRASE = "ende"

# MODEL_PATH = "../etc/models/vosk-model-de-0.21"
MODEL_PATH = "../etc/models/vosk-model-small-de-0.15"
WAITING_FOR_TRIGGER_SOUND = "../etc/sound/recoListening.wav"
TRIGGER_DETECTED_SOUND = "../etc/sound/recoSuccess.wav"
QUIT_SOUND = "../etc/sound/recoSleep.wav"
CREDENTIALS_PATH = "../etc/credentials.txt"


SAMPLE_RATE = 16000
CHUNK_SIZE = 2048
AUDIO_FORMAT = pyaudio.paInt16
TIMEOUT = 15


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AskAi:
    def __init__(self, api_key: str):
        openai.api_key = api_key
        self.msg_history: List[Dict[str, str]] = []

    def reset_chat(self):
        self.msg_history.clear()

    def ask_ai(self, prompt: str) -> str:
        """
        @brief Generates a response from an AI model for the given prompt using the OpenAI API.

        @param prompt: The prompt or question for which the AI should generate a response.

        @return The AI-generated response as a string.

        """
        user_message = {"role": "user", "content": f"Fasse dich kurz: {prompt}"}

        self.msg_history.append(user_message)

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.msg_history,
                temperature=0.3,
                max_tokens=300
            )

            if "error" in response:
                return str(response.error.message)

            ai_message = response.choices[0].message
            self.msg_history.append(ai_message)

            return str(ai_message.content)

        except openai.OpenAIError as e:
            return str(e)


def play_wav(filename):
    """
    @brief Plays a WAV audio file using the PyAudio library.

    @param filename: The path to the WAV file that should be played.
    """
    chunk = 1024

    wf = wave.open(filename, 'rb')

    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    data = wf.readframes(chunk)
    while data:
        stream.write(data)
        data = wf.readframes(chunk)

    stream.close()
    p.terminate()


def detect_trigger(recognizer: KaldiRecognizer, stream: pyaudio.Stream, trigger_phrase: str) -> bool:
    """
    @brief Detects a specified trigger phrase in the audio stream using the KaldiRecognizer.

    @param recognizer: The KaldiRecognizer object used for speech recognition.
    @param stream: The PyAudio Stream object representing the audio input stream.
    @param trigger_phrase: The trigger phrase to detect in the audio stream.

    @return True if the trigger phrase is detected, otherwise False.
    """
    data = stream.read(CHUNK_SIZE)
    if len(data) == 0:
        return False

    if recognizer.AcceptWaveform(data):
        result_json = json.loads(recognizer.Result())
        text = result_json['text']

    else:
        partial_result_json = json.loads(recognizer.PartialResult())
        text = partial_result_json['partial']

    if trigger_phrase.lower() in text.lower():
        return True

    return False


def speech_to_text(recognizer: KaldiRecognizer, stream: pyaudio.Stream) -> str:
    """
    @brief Transcribes speech from an audio stream to text using the KaldiRecognizer.

    @param recognizer: The KaldiRecognizer object used for speech recognition.
    @param stream: The PyAudio Stream object representing the audio input stream.

    @return The transcribed text from the audio stream as a string.
    """
    duration = time.time()
    while True:
        data = stream.read(CHUNK_SIZE)
        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            result = json.loads(result)
            result = result["text"]
            if not result:
                continue
            return result

        if time.time() - duration > TIMEOUT:
            return str()


def main() -> None:
    """
    @brief Main function to run the voice-activated chatbot using the Vosk and OpenAI APIs.

    Sets up the necessary components, such as the KaldiRecognizer, PyAudio, and the TTS engine.
    Listens for the trigger phrase, then transcribes speech and generates responses using the OpenAI API.
    Return to wait for the trigger phrase, listening and responding until the termination phrase is detected.
    """
    with open(CREDENTIALS_PATH, 'r') as json_file:
        json_data = json.load(json_file)
        openai_key = json_data["openai_api"]

    if not os.path.exists(MODEL_PATH):
        logger.error("Model existiert nicht.")
        sys.exit(1)

    model = Model(MODEL_PATH)
    ask_ai = AskAi(openai_key)

    recognizer = KaldiRecognizer(model, SAMPLE_RATE)
    tts_engine = pyttsx4.init()
    voice = tts_engine.getProperty("voices")

    tts_engine.setProperty('rate', 150)
    tts_engine.setProperty('voice', voice[0].id)

    audio = pyaudio.PyAudio()
    stream = audio.open(format=AUDIO_FORMAT, channels=1, rate=SAMPLE_RATE, input=True, frames_per_buffer=CHUNK_SIZE)

    play_wav(WAITING_FOR_TRIGGER_SOUND)
    is_active = True
    while is_active:
        if detect_trigger(recognizer, stream, TRIGGER_PHRASE):
            recognizer.Reset()

            play_wav(TRIGGER_DETECTED_SOUND)
            logger.info("Trigger detected. Listening...")

            while True:
                stt_text = speech_to_text(recognizer, stream)

                if stt_text:
                    logger.info(f"> {stt_text}")

                    if QUIT_TRIGGER_PHRASE.lower() in stt_text.lower():
                        is_active = False
                        break
                    elif stt_text.count(" ") > 2:
                        ai_reply = ask_ai.ask_ai(stt_text).replace("\n", "")

                        logger.info(f"< {ai_reply}")
                        tts_engine.say(ai_reply)
                        tts_engine.runAndWait()
                else:
                    ask_ai.reset_chat()
                    break

            play_wav(WAITING_FOR_TRIGGER_SOUND)

    stream.stop_stream()
    stream.close()
    audio.terminate()

    logger.info("End.")
    play_wav(QUIT_SOUND)


if __name__ == "__main":
    main()
