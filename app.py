import sys
import openai
import streamlit as st
import PyPDF2
import docx
import io
from pptx import Presentation
from pydub import AudioSegment
import requests
import time

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
        file_format = uploaded_file.type.split('/')[-1]
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format=file_format)
        audio_segment = audio_segment.set_frame_rate(16000)
        audio_file = io.BytesIO()
        audio_segment.export(audio_file, format="wav")
        audio_file.seek(0)
        audio_file.name = "audio.wav"
        return audio_file

def transcribe_audio(audio_file):
    assembly_key = st.secrets["assemblyai"]["api_key"]
    headers = {"authorization": assembly_key, "content-type": "application/json"}
    upload_endpoint = "https://api.assemblyai.com/v2/upload"
    transcription_endpoint = "https://api.assemblyai.com/v2/transcript"
    with open(audio_file.name, "rb") as f:
        response = requests.post(upload_endpoint, headers=headers, data=f)
        audio_url = response.json()["upload_url"]
    payload = {"audio_url": audio_url}
    response = requests.post(transcription_endpoint, headers=headers, json=payload)
    job_id = response.json()["id"]
    while True:
        response = requests.get(f"{transcription_endpoint}/{job_id}", headers=headers)
        status = response.json()["status"]
        if status == "completed":
            transcript = response.json()["text"]
            break
        elif status == "error":
            transcript = "Error occurred during transcription."
            break
        time.sleep(5)
    return transcript

def batch_messages(messages, max_tokens=16385):
    batches = []
    current_batch = []
    current_token_count = 0
    for message in messages:
        message_tokens = len(openai.LayoutLMv2.tokenize(message["content"])["tokens"])
        if current_token_count + message_tokens > max_tokens:
            batches.append(current_batch)
            current_batch = []
            current_token_count = 0
        current_batch.append(message)
        current_token_count += message_tokens
    if current_batch:
        batches.append(current_batch)
    return batches

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
        st.session_state.messages.append({"role": "system", "content": context_document})
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            message_batches = batch_messages(st.session_state.messages)
            for batch in message_batches:
                for response in openai.ChatCompletion.create(
                    model=st.session_state["openai_model"],
                    messages=batch,
                    stream=True,
                ):
                    full_response += response.choices[0].delta.get("content", "")
                    message_placeholder.markdown(full_response + "▌", unsafe_allow_html=True)
            message_placeholder.markdown(full_response, unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

if "messages" not in st.session_state:
    st.session_state.messages = []
uploaded_file = st.file_uploader("Upload your document or audio file here", type=["pdf", "docx", "ppt", "pptx", "txt", "mp3", "wav", "m4a"])
context_document = ""
if uploaded_file is not None:
    context_document = handle_uploaded_file(uploaded_file)
audio_file = handle_audio_data(uploaded_file)
if audio_file is not None:
    transcript = transcribe_audio(audio_file)
    st.write(transcript)
prompt = st.chat_input("What is this document about?")
handle_chat(prompt, context_document)

