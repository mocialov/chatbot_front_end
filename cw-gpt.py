import streamlit as st
from streamlit_chat import message
from PIL import Image
import requests
import io
import soundfile as sf
import os
from streamlit.runtime import get_instance
from streamlit.runtime.scriptrunner import get_script_run_ctx

def get_session():
    runtime = get_instance()
    session_id = get_script_run_ctx().session_id
    session_info = runtime._session_mgr.get_session_info(session_id)
    if session_info is None:
        return "default"
    return session_info.session

st.set_page_config(layout="wide")
st.title(os.environ["CW_CHATBOT_NAME"]+" ChatBot vs "+ get_session())

if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []

def generate_response(prompt):
    response = requests.post(os.environ["CW_SERVER_STREAMLIT"], json={'event':{'text': prompt}})

    audio_data = sf.read(io.BytesIO(response.content))[0]
    text_data = response.headers['Bot-Response-Text']
    return audio_data, text_data

def get_text():
    input_text = st.text_input("","", key="input")
    if input_text != "": st.session_state['past'].append(input_text)
    return input_text

user_input = get_text()

if user_input:
    output_audio, output_text = generate_response(user_input)
    st.session_state['generated'].append((output_audio, output_text))

if st.session_state['generated']:
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        st.audio(st.session_state["generated"][i][0], sample_rate=44100)
        message(st.session_state["generated"][i][1], key=str(i), avatar_style="initials", seed="AI")
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user', avatar_style="personas", seed=4)