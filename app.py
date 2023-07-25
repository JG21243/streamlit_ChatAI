import sys
import openai
import streamlit as st
import PyPDF2
import docx
import io
from pptx import Presentation
from pydub import AudioSegment

st.title("Josh's AI Assistant")
openai.api_key = st.secrets["openai"]["api_key"]

def handle_uploaded_file(uploaded_file):
    text = ""
    if uploaded_file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text()
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(io.BytesIO(uploaded_file.read()))
        text = "\n".join([para.text for para in doc.paragraphs])
    elif uploaded_file.type in ["application/vnd.ms-powerpoint", "application/vnd.openxmlformats-officedocument.presentationml.presentation"]:
        prs = Presentation(io.BytesIO(uploaded_file.read()))
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text += shape.text
    elif uploaded_file.type == "text/plain":
        text = uploaded_file.read().decode("utf-8")
    return f"Document: {text}"

def handle_audio_data(uploaded_file):
    audio_data = None
    if uploaded_file is not None and uploaded_file.type in ["audio/mp3", "audio/wav", "audio/m4a"]:
        audio_data = uploaded_file.read()

    if audio_data is not None:
        # Convert the audio data to WAV format with 16 kHz
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format="webm")
        audio_segment = audio_segment.set_frame_rate(16000)
        audio_file = io.BytesIO()
        audio_segment.export(audio_file, format="wav")
        audio_file.seek(0)
        audio_file.name = "audio.wav"
        return audio_file

def transcribe_audio(audio_file):
    # Transcribe the audio using the Whisper API
    with st.spinner("Transcribing audio..."):
        transcript = openai.Audio.transcribe(
            file=audio_file,
            model="whisper-1",
            response_format="text",
            language="en"
        )
    return transcript

def handle_chat(prompt, context_document):
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo-16k"

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Add the context document as a system message
        st.session_state.messages.append({"role": "system", "content": context_document})

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for response in openai.ChatCompletion.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            ):
                full_response += response.choices[0].delta.get("content", "")
                message_placeholder.markdown(full_response + "▌", unsafe_allow_html=True)
            message_placeholder.markdown(full_response, unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# Initializing session state
if "messages" not in st.session_state:
    st.session_state.messages = []

uploaded_file = st.file_uploader("Upload your document or audio file here", type=["pdf", "docx", "ppt", "pptx", "txt", "mp3", "wav", "m4a"])

context_document = ""
if uploaded_file is not None:
    context_document = handle_uploaded_file(uploaded_file)

audio_file = handle_audio_data(uploaded_file)

if audio_file is not None:
    transcript = transcribe_audio(audio_file)
    st.write(transcript["text"])

prompt = st.chat_input("What is up?")
handle_chat(prompt, context_document)
