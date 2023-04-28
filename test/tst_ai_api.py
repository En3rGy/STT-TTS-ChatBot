import unittest
import stt
import json
import logging

from stt import AskAi


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        with open("../etc/credentials.txt", 'r') as json_file:
            json_data = json.load(json_file)
            key = json_data["openai_api"]

        self.ask_ai = stt.AskAi(key)

    def test_ask_ai(self):
        self.logger.info("### test_ask_ai ###")

        ret = self.ask_ai.ask_ai("Wenn ich dir signalisiere, dass der Chat fertig ist, antworte nur '#Ende'.")
        self.logger.info(ret)
        self.assertTrue(ret)

        ret = self.ask_ai.ask_ai("Wann und wo lebte Martin Luther?")
        self.logger.info(ret)
        self.assertTrue(ret)

        ret = self.ask_ai.ask_ai("Danke das wars")
        self.logger.info(ret)
        self.assertEqual(ret, "#Ende")

    def test_completion(self):
        self.logger.info("### test_completion ###")

        error_request = "au der stuhl a wackelte was könnte önnte der grund ein"
        ret = self.ask_ai.ask_ai(error_request)
        self.logger.info(ret)
        self.assertTrue(ret)


if __name__ == '__main__':
    unittest.main()
