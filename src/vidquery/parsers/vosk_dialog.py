import os
from videogrep.transcribe import transcribe
from ..models import Clip

PARSER_NAME = "vosk"
PARSER_LONG_NAME = "Vosk Speech-to-Text"
PARSER_CAT = "dialog"
PARSER_SUBCATS = ["vosk_sentence", "vosk_word"]
PARSER_DESCRIPTION = "Transcribes speech in a video using Vosk."


def process(video, options={}):
    transcript_file = os.path.splitext(video)[0] + ".json"
    results = []

    segments = transcribe(video)

    sentences = []
    words = []

    for s in segments:
        sentences.append(Clip(content=s["content"], start=s["start"], end=s["end"]))
        for w in s["words"]:
            words.append(Clip(content=w["word"], start=w["start"], end=w["end"]))

    results.append((PARSER_NAME, PARSER_CAT, "vosk_sentence", sentences))
    results.append((PARSER_NAME, PARSER_CAT, "vosk_word", words))

    if os.path.exists(transcript_file):
        try:
            os.remove(transcript_file)
        except Exception as _:
            pass

    return results
