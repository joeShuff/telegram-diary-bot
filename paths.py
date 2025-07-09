import datetime


def get_filenames_format() -> str:
    now = datetime.datetime.now()
    timestamp = int(now.timestamp())
    formatted_date = now.strftime("%d_%m_%Y_%H_%M")

    return f"{formatted_date}_{timestamp}"


def get_audio_filename() -> str:
    return get_filenames_format() + ".ogg"


def get_transcription_filename() -> str:
    return get_filenames_format() + ".txt"
