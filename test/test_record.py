import pyaudio
import wave

RATE = 8000
CHUNK = 2048
# RATE = 16000

def record_audio(file_path, duration, device_index=None):
    audio = pyaudio.PyAudio()
        
    info = audio.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')    
    for i in range(0, numdevices):
        device_info = audio.get_device_info_by_index(i)
        if "seeed-8mic-voicecard" in device_info["name"]:
            print("Found Seeed-8mic on indec {}".format(device_info["index"]))
            device_index = device_info["index"]
        break
    
    device_info = audio.get_device_info_by_index(device_index) if device_index else None
    stream = audio.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=RATE,
        # rate=int(device_info['defaultSampleRate']) if device_info else None,
        input=True,
        input_device_index=device_info['index'] if device_info else None,
        frames_per_buffer=CHUNK
    )

    print("### Recording ###")
    frames = []
    for _ in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    audio.terminate()

    wave_file = wave.open(file_path, 'wb')
    wave_file.setnchannels(1)
    wave_file.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
    wave_file.setframerate(RATE)
    wave_file.writeframes(b''.join(frames))
    wave_file.close()
    
# Example usage
file_path = './recording.wav'
duration = 5  # Duration in seconds
device_index = 1  # The index of the desired audio input device
record_audio(file_path, duration, device_index)
