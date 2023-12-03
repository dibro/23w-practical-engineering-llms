#from langchain.schema import AIMessage, HumanMessage
import gradio as gr
import json
import requests

def get_response_from_llm(user_input):
    url = "http://localhost:11434/api/generate"
    headers = {
        "Content-Type": "application/json",
    }
    data = json.dumps({
        "model": "llama2",
        "prompt": user_input,
        "stream": False,
    })
    # Make the request
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        answer = json.loads(response.text)['response']
    else: 
        answer = response.reason
    return answer 

def predict(message, history):
    history = ""
    for human, ai in history:
        history += f"Human: {human}"
        history += f"AI: {ai}"
    history += f"Human: {message}"
    history += "AI:"
    print(history)
    answer = get_response_from_llm(history)
    return answer

demo = gr.ChatInterface(predict,
    chatbot=gr.Chatbot(height=300),
    textbox=gr.Textbox(placeholder="Ask me anything", container=False, scale=7),
    title="Talk to llama2",
    description="Ask me anything",
    ).launch()

if __name__ == "__main__":
    demo.launch(show_api=False)  