import whisper
from deep_translator import GoogleTranslator


def transcribe_audio(file_path_micro, selected_language):
    model = whisper.load_model("base")
    result = model.transcribe(file_path_micro)
    translated_question = GoogleTranslator(source='auto', target=selected_language).translate(result["text"])
    response = answer_the_question(translated_question, selected_language)
    return response


def answer_the_question(question, selected_language):
    answer_to_return = answer(question, selected_language)
    translated_answer = GoogleTranslator(source='auto', target=selected_language).translate(answer_to_return)
    return translated_answer


def answer(question, selected_language):
    answer_for_question = 'Пока я не умею отвечать на вопросы'
    return answer_for_question
