import unittest
import stt
import json
import logging
import os
import pyttsx3

from stt import AskAi


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        # Set the proxy configuration
        http_proxy = ""
        https_proxy = ""

        os.environ["HTTP_PROXY"] = http_proxy
        os.environ["HTTPS_PROXY"] = https_proxy

    def test_ask_ai(self):
        self.logger.info("### test_ask_ai ###")
        with open("../etc/credentials.txt", 'r') as json_file:
            json_data = json.load(json_file)
            key = json_data["openai_api"]

        self.ask_ai = stt.AskAi(key)

        ret = self.ask_ai.ask_ai("Beende jede Antwort mit '#Ende'.")
        self.logger.info(ret)
        self.assertTrue(ret)

        ret = self.ask_ai.ask_ai("Wann und wo lebte Martin Luther?")
        self.logger.info(ret)
        self.assertTrue(ret)

        ret = self.ask_ai.ask_ai("Danke das wars")
        self.logger.info(ret)
        self.assertTrue("#Ende" in ret)

    def test_completion(self):
        self.logger.info("### test_completion ###")
        with open("../etc/credentials.txt", 'r') as json_file:
            json_data = json.load(json_file)
            key = json_data["openai_api"]

        self.ask_ai = stt.AskAi(key)
        error_request = "au der stuhl a wackelte was könnte önnte der grund ein"
        ret = self.ask_ai.ask_ai(error_request)
        self.logger.info(ret)
        self.assertTrue(ret)

    def test_play_wav(self):
        self.logger.info("### test_play_wav")

        stt.play_wav("../etc/sound/recoSuccess.wav")
        self.assertTrue(True)

    def test_tts(self):
        tts_engine = pyttsx3.init()
        voice = tts_engine.getProperty("voices")

        tts_engine.setProperty('rate', 150)
        tts_engine.setProperty('voice', voice[0].id)
        tts_engine.say("The quick brown fox jumps over the lazy dog.")
        tts_engine.runAndWait()
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
