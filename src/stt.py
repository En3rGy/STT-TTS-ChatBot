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
# import pyttsx3.drivers.sapi5
import openai
from vosk import Model, KaldiRecognizer

sys.path.append("../3rd_party/pixel_ring/pixel_ring")

import apa102
from gpiozero import LED


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
SAMPLE_RATE_IN = 22050
CHUNK_SIZE = 2048
# CHUNK_SIZE = 1024
AUDIO_FORMAT = pyaudio.paInt16
TIMEOUT = 15
AUDIO_OUT_IDX = 0
AUDIO_IN_IDX = 2

logging.basicConfig(filename='log.log', encoding='utf-8', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
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
        logger.debug(user_message)

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


class LedPattern:
    NUM_LED = 12

    def __init__(self):
        self.power = LED(5)
        self.power.on()
        self.leds = apa102.APA102(num_led=self.NUM_LED)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.leds.clear_strip()
        self.power.off()

    def show_color(self, r, g, b, m=-1):
        if m == -1:
            for n in range(self.NUM_LED):
                self.leds.set_pixel(n, r, g, b)
                self.leds.show()
        else:
            self.leds.set_pixel(m, r, g, b)
            self.leds.show()

    def clear_strip(self):
        self.leds.clear_strip()


def play_wav(filename, device_index=None):
    """
    @brief Plays a WAV audio file using the PyAudio library.

    @param filename: The path to the WAV file that should be played.
    @param device_index:
    """
    chunk = 1024

    logger.info("Opening file")
    wf = wave.open(filename, 'rb')

    logger.info("Creating pyaudio")
    p = pyaudio.PyAudio()

    device_info = p.get_device_info_by_index(device_index) if device_index else None

    logger.debug("Playing wav file using {}".format(device_info))

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


class SttHandler:
    CHUNK_SIZE = 2048

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # init audio in
        self.audio = pyaudio.PyAudio()
        info = self.audio.get_host_api_info_by_index(0)
        num_devices = info.get('deviceCount')
        logger.debug("Found {} devices".format(num_devices))
        device_index = None
        for i in range(0, num_devices):
            device_info = self.audio.get_device_info_by_index(i)
            self.logger.debug(device_info)
            if "seeed-8mic-voicecard" in device_info["name"]:
                self.logger.debug("Found Seeed-8mic on indec {}".format(device_info["index"]))
                device_index = int(device_info["index"])
                break

        if device_index is None:
            assert "Seeed not found"

        device_info = self.audio.get_device_info_by_index(device_index)
        self.logger.debug("Recording audio using {}".format(device_info))
        self.stream = self.audio.open(format=AUDIO_FORMAT,
                                      channels=1,
                                      rate=SAMPLE_RATE_IN,
                                      # rate=int(device_info['defaultSampleRate']), 
                                      input=True,
                                      input_device_index=device_info['index'] if device_info else None,
                                      frames_per_buffer=self.CHUNK_SIZE)

    def __del__(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

    def detect_trigger(self, recognizer: KaldiRecognizer, trigger_phrase: str) -> bool:
        """
        @brief Detects a specified trigger phrase in the audio stream using the KaldiRecognizer.

        @param recognizer: The KaldiRecognizer object used for speech recognition.
        @param trigger_phrase: The trigger phrase to detect in the audio stream.

        @return True if the trigger phrase is detected, otherwise False.
        """
        self.logger.debug("detect_trigger")
        while True:
            frames = []
            data = self.stream.read(self.CHUNK_SIZE, False)

            if not data or len(data) == 0:
                return False

            if recognizer.AcceptWaveform(data):
                result_json = json.loads(recognizer.Result())
                text = result_json['text']
                self.logger.debug("Result: '{}'".format(text)) if text else True

            else:
                partial_result_json = json.loads(recognizer.PartialResult())

                text = partial_result_json['partial']
                self.logger.debug("Partial: '{}'".format(text)) if text else True

            if trigger_phrase.lower() in text.lower():
                return True

    def speech_to_text(self, recognizer: KaldiRecognizer) -> str:
        """
        @brief Transcribes speech from an audio stream to text using the KaldiRecognizer.

        @param recognizer: The KaldiRecognizer object used for speech recognition.
        @param stream: The PyAudio Stream object representing the audio input stream.

        @return The transcribed text from the audio stream as a string.
        """
        duration = time.time()
        while True:
            data = self.stream.read(self.CHUNK_SIZE, False)
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

    logger.info("\t\t\t#### Start main ####")

    leds = LedPattern()
    leds.show_color(1, 0, 0, 1)

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

    leds.show_color(1, 0, 0, 2)
    model = Model(model_path)
    ask_ai = AskAi(openai_key)

    leds.show_color(1, 0, 0, 3)
    stt_handler = SttHandler()

    leds.show_color(1, 0, 0, 4)
    recognizer = KaldiRecognizer(model, SAMPLE_RATE_IN)
    tts_engine = pyttsx3.init()
    voices = tts_engine.getProperty("voices")
    voice_id = 0
    for voice in voices:
        logger.debug("Id: {}, name: {}, complete: {}".format(voice.id, voice.name, voice))
        if "german-mbrola-5" in voice.name:
            voice_id = voice.id

    tts_engine.setProperty('rate', 150)
    tts_engine.setProperty('voice', voice_id)

    leds.show_color(1, 0, 0, 5)
    play_wav(waiting_for_trigger_sound, AUDIO_OUT_IDX)
    is_active = True

    logger.info("Entering loop...")

    leds.clear_strip()
    try:
        while is_active:
            if stt_handler.detect_trigger(recognizer, trigger_phrase):
                leds.show_color(0, 1, 0)

                recognizer.Reset()

                play_wav(trigger_detected_sound, AUDIO_OUT_IDX)
                logger.info("Trigger detected. Listening...")

                while True:
                    leds.show_color(1, 1, 0)

                    stt_text = stt_handler.speech_to_text(recognizer)

                    if stt_text:
                        logger.info(f"> {stt_text}")

                        if quit_trigger_phrase.lower() in stt_text.lower():
                            is_active = False
                            break
                        elif stt_text.count(" ") > 2:
                            leds.show_color(1, 0, 0)

                            ai_reply = ask_ai.ask_ai(stt_text)
                            logger.info("< {}".format(ai_reply.replace("\n", "")))
                            tts_engine.say(ai_reply)
                            tts_engine.runAndWait()
                    else:
                        leds.clear_strip()

                        ask_ai.reset_chat()
                        break

                leds.clear_strip()
                play_wav(waiting_for_trigger_sound, AUDIO_OUT_IDX)

        logger.info("End.")
        play_wav(quit_sound, AUDIO_OUT_IDX)

    finally:
        pass


if __name__ == "__main__":
    logger.info(f"{__file__}:{__name__}")
    main()
