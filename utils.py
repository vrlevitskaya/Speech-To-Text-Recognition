import whisper


def transcribe_audio(languages, file_path_micro):
    model = whisper.load_model("base")
    result = model.transcribe(file_path_micro)
    answered_question = answer_the_question(languages, result["text"])
    return result["text"], answered_question


def answer_the_question(languages,question):
    return f'Привет: {question}'

