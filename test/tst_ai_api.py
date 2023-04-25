import unittest
import stt
import json
import logging


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

    def test_ask_ai(self):
        self.logger.info("### test_ask_ai ###")
        with open("../etc/credentials.txt", 'r') as json_file:
            json_data = json.load(json_file)
            key = json_data["openai_api"]

        ret = stt.ask_ai("Wann und wo lebte Martin Luther?", key)
        self.logger.info(ret)
        self.assertTrue(ret)  # add assertion here


if __name__ == '__main__':
    unittest.main()
