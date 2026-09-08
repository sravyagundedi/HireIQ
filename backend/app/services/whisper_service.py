from functools import lru_cache
import whisper
from ..config import get_settings


@lru_cache(maxsize=2)
def get_model():
    settings = get_settings()
    return whisper.load_model(settings.whisper_model)


def transcribe_audio(path: str) -> str:
    result = get_model().transcribe(path)
    return result["text"].strip()
