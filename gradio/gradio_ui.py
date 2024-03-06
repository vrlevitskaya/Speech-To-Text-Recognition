import gradio as gr
from deep_translator import GoogleTranslator
from utils import transcribe_audio, answer_the_question

available_languages = GoogleTranslator().get_supported_languages()

audio_input = gr.Audio(type="filepath", label="Ask Your Question", sources=["microphone"])
text_input = gr.Textbox(label="Ask Your Question")
transcribed_question = gr.Textbox(label="Here your transcribed question")
answer_text_tab1 = gr.Textbox(label="Answer for your question")
answer_text_tab2 = gr.Textbox(label="Answer for your question")
dropdown_with_languages_tab1 = gr.Dropdown(choices=available_languages, label="Choose language to translate in")
dropdown_with_languages_tab2 = gr.Dropdown(choices=available_languages, label="Choose language to translate in")

speech_to_text = gr.Interface(fn=transcribe_audio, inputs=[dropdown_with_languages_tab1, audio_input],
                              outputs=[transcribed_question, answer_text_tab1],
                              title="ChatBot for applicants",
                              allow_flagging="never")
text_to_text = gr.Interface(fn=answer_the_question, inputs=[dropdown_with_languages_tab2, text_input],
                            outputs=[answer_text_tab2],
                            title="ChatBot for applicants",
                            allow_flagging="never")

demo = gr.TabbedInterface([speech_to_text, text_to_text], ["Speech-to-text", "Text-to-text"])

