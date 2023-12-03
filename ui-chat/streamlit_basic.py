import streamlit as st
from streamlit_chat import message
from streamlit.components.v1 import html
import requests
import json

# Set the URL and headers for the request
url = "http://localhost:11434/api/generate"
headers = {
    "Content-Type": "application/json",
}

def on_input_change():
    user_input = st.session_state.user_input
    st.session_state.past.append(user_input)
    data = json.dumps({
        "model": "llama2",
        "prompt": user_input,
        "stream": False,
    })
    # Make the request
    response = requests.post(url, headers=headers, data=data)
    st.session_state.generated.append(json.loads(response.text)['response'])

    # if response.status_code == 200:
    #     print("Response:", response.text)
    # else:
    #     print("Error:", response.reason)

def on_btn_click():
    del st.session_state.past[:]
    del st.session_state.generated[:]

st.session_state.setdefault(
    'past', 
    []
)
st.session_state.setdefault(
    'generated', 
    []
)

st.title("Chat placeholder")

chat_placeholder = st.empty()

with chat_placeholder.container():   
     
    for i in range(len(st.session_state['generated'])):                
        message(st.session_state['past'][i], is_user=True, key=f"{i}_user")
        message(st.session_state['generated'][i], key=f"{i}")
        # message(
        #     st.session_state['generated'][i]['data'], 
        #     key=f"{i}", 
        #     allow_html=True,
        #     is_table=True if st.session_state['generated'][i]['type']=='table' else False
        # )
    st.button("Clear message", on_click=on_btn_click)

with st.container():
    st.text_input("User Input:", on_change=on_input_change, key="user_input")
