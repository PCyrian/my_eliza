import pyaudio
import wave
from utilities import save_wave_as_mp3

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
WAVE_RECORDING_FILENAME = "temp_files/temp.wav"
MP3_RECORDING_FILENAME = "temp_files/temp.mp3"

class Audio:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.output = MP3_RECORDING_FILENAME

    def list_audio_input_devices(self):
        info = self.p.get_host_api_info_by_index(0)
        num_devices = info.get('deviceCount')
        devices = []
        for i in range(num_devices):
            device_info = self.p.get_device_info_by_host_api_device_index(0, i)
            if device_info.get('maxInputChannels') > 0:
                devices.append(device_info.get('name'))
        return devices

    def start_recording(self, microphone_index):
        self.stream = self.p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True,
                                  input_device_index=microphone_index, frames_per_buffer=CHUNK)
        self.frames = []
        print("Recording started...")

    def stop_recording(self):
        self.stream.stop_stream()
        self.stream.close()
        self.stream = None
        with wave.open(WAVE_RECORDING_FILENAME, 'wb') as wave_file:
            wave_file.setnchannels(CHANNELS)
            wave_file.setsampwidth(self.p.get_sample_size(FORMAT))
            wave_file.setframerate(RATE)
            wave_file.writeframes(b''.join(self.frames))
        print("Recording stopped...")

    def record(self):
        while self.stream.is_active():
            data = self.stream.read(CHUNK)
            self.frames.append(data)

    def save_wave_as_mp3(self):
        save_wave_as_mp3(WAVE_RECORDING_FILENAME, MP3_RECORDING_FILENAME)
