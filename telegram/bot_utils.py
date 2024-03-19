import whisper
from deep_translator import GoogleTranslator
from parser import get_text_from_google
from telegram.gpt import generate_answer, write_questions_to_docx

def transcribe_audio(file_path_micro, selected_language, campus='Moscow'):
    model = whisper.load_model("base")
    result = model.transcribe(file_path_micro)
    translated_question = GoogleTranslator(source='auto', target='ru').translate(result["text"])
    response = answer_the_question(translated_question, selected_language, campus)
    write_questions_to_docx(result["text"], response)
    return response


def answer_the_question(question, selected_language, campus='Moscow'):
    full_question = question + "HSE University" + " campus"
    content = get_text_from_google(query=full_question)
    answer_to_return = generate_answer(question, campus, content)
    translated_answer = GoogleTranslator(source='auto', target=selected_language).translate(answer_to_return[0])
    return translated_answer

