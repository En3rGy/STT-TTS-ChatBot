
import pygame


def play_wav(file_path):
  pygame.mixer.init()
  pygame.mixer.music.set_volume(0.5)
  pygame.mixer.music.load(file_path)
  pygame.mixer.music.play()


file_path = "../etc/sound/recoSleep.wav"
play_wav(file_path)
