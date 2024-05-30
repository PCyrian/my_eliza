from pydub import AudioSegment

def save_wave_as_mp3(wav_filename, mp3_filename):
    sound = AudioSegment.from_wav(wav_filename)
    sound.export(mp3_filename, format="mp3")
