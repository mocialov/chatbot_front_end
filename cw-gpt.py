import streamlit as st
from streamlit_chat import message
from PIL import Image
import requests
import io
import soundfile as sf
import os
import uuid
import extra_streamlit_components as stx

# st.set_page_config(layout="wide")

cookie_name = "my_cookie_name"
content = uuid.uuid4().hex

def get_manager():
    return stx.CookieManager()
cookie_manager = get_manager()

if cookie_manager.get(cookie=cookie_name) is None: cookie_manager.set(cookie_name, content)

st.title(os.environ["CW_CHATBOT_NAME"]+" ChatBot vs "+ cookie_manager.get(cookie=cookie_name))

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