import requests
import xml.etree.ElementTree as ET
import sys

sys.path.append("../src")

import dlnahelper

sonos = dlnahelper.DlnaHelper('192.168.143.105', 10)
sonos.play_uri('https://freetestdata.com/wp-content/uploads/2021/09/Free_Test_Data_5MB_MP3.mp3')
