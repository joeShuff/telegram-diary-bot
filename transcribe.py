from faster_whisper import WhisperModel

# Load once globally
model = WhisperModel("base", device="cpu", compute_type="int8")  # You can use "medium", "large", etc.


def transcribe_voice(file_path: str) -> str:
    segments, _ = model.transcribe(file_path)
    result = []
    for segment in segments:
        result.append(segment.text)
    return " ".join(result)
