
# Josh's AI Assistant

This is a Python script that uses the OpenAI API to create an AI assistant. The assistant can process text from documents and transcribe audio files. It uses the Streamlit library to create a web interface for user interaction.

## Dependencies

This script requires the following Python libraries:

- sys
- openai
- streamlit
- PyPDF2
- docx
- io
- pptx
- pydub

You can install these libraries using pip:

```bash
pip install openai streamlit PyPDF2 python-docx python-pptx pydub
```

## Usage

First, you need to set your OpenAI API key in the script:

```python
openai.api_key = 'your-api-key'
```
Please replace 'your-api-key' with your actual OpenAI API key. Make sure to keep your API key secret and do not share it with anyone.

Run the Streamlit app.

```bash
streamlit run your_script.py
```

Follow the instructions in the app to upload a file and interact with the chatbot.

You can upload a document (PDF, DOCX, PPT, PPTX, TXT) or an audio file (MP3, WAV, M4A), and the assistant will process the file and respond to your prompts.

## Features

- Document Processing: The assistant can read text from PDF, DOCX, PPT, PPTX, and TXT files. It uses the PyPDF2 library for PDF files, the docx library for DOCX files, and the pptx library for PPT and PPTX files.
- Audio Transcription: The assistant can transcribe audio from MP3, WAV, and M4A files. It uses the pydub library to process the audio files and the OpenAI Whisper API for transcription.
- Chat Interface: The assistant uses a chat interface for interaction. You can type your prompts in the chat input field, and the assistant will respond in the chat area. The assistant uses the OpenAI GPT-3.5-turbo model for generating responses.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Credits

This project uses code from:

- [OpenAI](https://openai.com/)
- [Streamlit](https://streamlit.io/)



