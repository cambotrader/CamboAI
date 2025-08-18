import streamlit as st
import requests
import speech_recognition as sr

st.set_page_config(page_title='Cambo AI', layout='centered')
st.title('🌍 Cambo AI Agent Playground')

# Agent selector
agent = st.selectbox('Choose an agent:', ['Trader', 'Educator', 'Media Assistant'])

# Voice input (optional)
use_voice = st.checkbox('Use voice input')
user_input = ''

if use_voice:
    st.info('Listening... (requires microphone access)')
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
        try:
            user_input = recognizer.recognize_google(audio)
            st.success(f'You said: {user_input}')
        except sr.UnknownValueError:
            st.error('Could not understand audio')
        except sr.RequestError:
            st.error('Voice recognition failed')

else:
    user_input = st.text_input('Enter your query')

# Run agent
if st.button('Run Agent') and user_input:
    payload = {
        "agent": agent.lower(),
        "input": user_input
    }
    try:
        response = requests.post("https://api.camboai.com/agent", json=payload)
        st.write(response.json())
    except Exception as e:
        st.error(f"Error: {e}")
