import unittest
import stt
import json
import logging


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        with open("../etc/credentials.txt", 'r') as json_file:
            json_data = json.load(json_file)
            self.key = json_data["openai_api"]

    def test_ask_ai(self):
        self.logger.info("### test_ask_ai ###")

        ret = stt.ask_ai("Wann und wo lebte Martin Luther?", self.key)
        self.logger.info(ret)
        self.assertTrue(ret)  # add assertion here

    def test_completion(self):
        self.logger.info("### test_completion ###")

        error_request = "au der stuhl a wackelte was könnte önnte der grund ein"
        ret = stt.ask_ai(error_request, self.key)
        self.logger.info(ret)
        self.assertTrue(ret)


if __name__ == '__main__':
    unittest.main()
