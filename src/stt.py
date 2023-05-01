import sys
import time
import json
import wave
import logging
from typing import List, Dict
import configparser
import os

import pyaudio
import pyttsx3
import pyttsx3.driver
import pyttsx3.drivers.sapi5
import openai
from vosk import Model, KaldiRecognizer


def resource_path(relative_path: str) -> str:
    try:
        # PyInstaller erstellt während der Ausführung einen tempor?ren Ordner, auf den diese Umgebungsvariable verweist
        base_path = sys._MEIPASS
    except Exception:
        # Wenn die Anwendung nicht durch PyInstaller gebündelt ist, verwenden Sie den normalen relativen Pfad
        base_path = os.path.dirname(os.path.abspath(__file__)) + "/.."

    return os.path.join(base_path, relative_path)


# Constants
CONFIG_FILE = resource_path("etc/config.ini")
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

    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    credentials_path = resource_path(config.get("settings", "credential_path", fallback="etc/credentials.txt"))
    trigger_phrase = config.get("settings", "trigger_phrase", fallback="hey computer")
    quit_trigger_phrase = config.get("settings", "quit_trigger_phrase", fallback="ende")
    waiting_for_trigger_sound = resource_path(config.get("sound", "waiting_for_trigger_sound",
                                                         fallback="etc/sound/recoListening.wav"))
    trigger_detected_sound = resource_path(config.get("sound", "trigger_detect_sound",
                                                      fallback="etc/sound/recoSuccess.wav"))
    quit_sound = resource_path(config.get("sound", "quit_sound", fallback="etc/sound/recoSleep.wav"))
    model_path = resource_path(config.get("vosk", "model_path", fallback="etc/model/vosk-model-small-de-0.15"))
    http_proxy = config.get("poxy", "http", fallback="")
    https_proxy = config.get("proxy", "https", fallback="")

    os.environ["HTTP_PROXY"] = http_proxy
    os.environ["HTTPS_PROXY"] = https_proxy

    if not os.path.exists(CONFIG_FILE):
        config.add_section("settings")
        config.set("settings", "trigger_phrase", trigger_phrase)
        config.set("settings", "quit_trigger_phrase", quit_trigger_phrase)
        config.set("settings", "credential_path", credentials_path)

        config.add_section("sound")
        config.set("sound", "waiting_for_trigger_sound", waiting_for_trigger_sound)
        config.set("sound", "trigger_detect_sound", trigger_detected_sound)
        config.set("sound", "quit_sound", quit_sound)

        config.add_section("vosk")
        config.set("vosk", "model_path", model_path)
        config.add_section("proxy")
        config.set("proxy", "http", http_proxy)
        config.set("proxy", "https", https_proxy)

        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)

    with open(credentials_path, 'r') as json_file:
        json_data = json.load(json_file)
        openai_key = json_data["openai_api"]

    if not os.path.exists(model_path):
        logger.error(f"Model {model_path} existiert nicht.")
        sys.exit(1)

    model = Model(model_path)
    ask_ai = AskAi(openai_key)

    recognizer = KaldiRecognizer(model, SAMPLE_RATE)
    tts_engine = pyttsx3.init()
    voice = tts_engine.getProperty("voices")

    tts_engine.setProperty('rate', 150)
    tts_engine.setProperty('voice', voice[0].id)

    audio = pyaudio.PyAudio()
    stream = audio.open(format=AUDIO_FORMAT, channels=1, rate=SAMPLE_RATE, input=True, frames_per_buffer=CHUNK_SIZE)

    play_wav(waiting_for_trigger_sound)
    is_active = True
    while is_active:
        if detect_trigger(recognizer, stream, trigger_phrase):
            recognizer.Reset()

            play_wav(trigger_detected_sound)
            logger.info("Trigger detected. Listening...")

            while True:
                stt_text = speech_to_text(recognizer, stream)

                if stt_text:
                    logger.info(f"> {stt_text}")

                    if quit_trigger_phrase.lower() in stt_text.lower():
                        is_active = False
                        break
                    elif stt_text.count(" ") > 2:
                        ai_reply = ask_ai.ask_ai(stt_text)
                        logger.info("< {}".format(ai_reply.replace("\n", "")))
                        tts_engine.say(ai_reply)
                        tts_engine.runAndWait()
                else:
                    ask_ai.reset_chat()
                    break

            play_wav(waiting_for_trigger_sound)

    stream.stop_stream()
    stream.close()
    audio.terminate()

    logger.info("End.")
    play_wav(quit_sound)


if __name__ == "__main__":
    logger.info(f"{__file__}:{__name__}")
    main()
