from pydub import AudioSegment
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
from deep_translator import GoogleTranslator

DetectorFactory.seed = 0


def save_wave_as_mp3(wav_filename, mp3_filename):
    sound = AudioSegment.from_wav(wav_filename)
    sound.export(mp3_filename, format="mp3")


def detect_language(transcription: str) -> str:
    try:
        language_code = detect(transcription)
        if language_code == "fr":
            return "fr"
        else:
            return "en"
    except LangDetectException:
        return "unknown"


def assure_language_continuity(chat_history: list[dict[str, str]], new_transcription: str) -> str:
    if not chat_history:
        return new_transcription
    last_entry_content = chat_history[-1]["content"]
    last_language = detect_language(last_entry_content)
    new_language = detect_language(new_transcription)
    if new_language != last_language:
        translated = GoogleTranslator(source=new_language, target=last_language).translate(new_transcription)
        return translated
    return new_transcription

