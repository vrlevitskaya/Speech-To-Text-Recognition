import whisper
from deep_translator import GoogleTranslator


def transcribe_audio(file_path_micro, languages=None):
    model = whisper.load_model("base")
    result = model.transcribe(file_path_micro)
    selected_language = languages.lower()
    response = answer_the_question(languages, result["text"])
    translated_question = GoogleTranslator(source='auto', target=selected_language).translate(result["text"])
    return translated_question, response


def answer_the_question(languages, question):
    selected_language = languages.lower()
    answer_to_return = answer(question)
    translated_answer = GoogleTranslator(source='auto', target=selected_language).translate(answer_to_return)
    return translated_answer


def answer(question):
    answer_for_question = 'Пока я не умею отвечать на вопросы'
    return answer_for_question
