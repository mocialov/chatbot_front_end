import streamlit as st
from streamlit_chat import message
import requests
import io
import soundfile as sf
import os
import uuid
import extra_streamlit_components as stx
import shortuuid
from load_css import local_css

local_css("style.css")

cookie_name = "user_id_cookie"
content = shortuuid.encode(uuid.uuid4())[:7]

cookie_manager = stx.CookieManager()

if cookie_manager.get(cookie=cookie_name) is None: cookie_manager.set(cookie_name, content)

col1, col2 = st.columns([3, 1], vertical_alignment="bottom")
col1.markdown(f"""
<h3>{os.environ["CW_CHATBOT_NAME"]} ChatBot vs {cookie_manager.get(cookie=cookie_name)}</h3>
""", unsafe_allow_html=True)
if "CW_CHATBOT_MODE" in os.environ and os.environ["CW_CHATBOT_MODE"] != "":
    col2.markdown(f"""
    <span class='highlight red'><span class='bold'>{os.environ["CW_CHATBOT_MODE"]}</span> </span>
    """, unsafe_allow_html=True)

if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []

def generate_response(prompt):

    try:

        response = requests.post(os.environ["CW_SERVER_STREAMLIT"], json={'event':{'text': prompt, 'user': cookie_manager.get(cookie=cookie_name), 'mode': os.environ["CW_CHATBOT_MODE"]}})

        print ("status", response.status_code)
        print (response.headers)

        audio_data = sf.read(io.BytesIO(response.content))[0]
        text_data = response.headers['Bot-Response-Text']
        return audio_data, text_data
    except Exception as e:
        print (e)
        return None, None

st.markdown(
    """
    <style>
    .stTextInput, .stButton {
        display: flex;
        align-items: flex-end;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def get_text():
    with st.form(key='input_form'):
        col1, col2 = st.columns([4, 1])
        with col1:
            input_text = st.text_input("","", key="input")
        with col2:
            col2_placeholder = st.empty()
            submit_button = col2_placeholder.form_submit_button(label='Send')
    if submit_button and input_text != "": 
        st.session_state['past'].append(input_text)
    return input_text if submit_button else None

user_input = get_text()

if user_input:
    output_audio, output_text = generate_response(user_input)
    if output_audio is not None and output_text is not None:
        st.session_state['generated'].append((output_audio, output_text))
    else:
        st.session_state['generated'].append((None, "No response from the server"))

if st.session_state['generated']:
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        if st.session_state["generated"][i][0] is not None:
            st.audio(st.session_state["generated"][i][0], sample_rate=44100)
        with st.chat_message("ai", avatar="🤖"):
            st.write(st.session_state["generated"][i][1])
        with st.chat_message("user", avatar="🤔"):
            st.write(st.session_state['past'][i])