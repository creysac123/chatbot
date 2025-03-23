import streamlit as st
import requests
from datetime import datetime

# API Key and URL from Streamlit secrets
API_KEY = st.secrets["API_KEY"]
API_URL = st.secrets["API_URL"]

# Ensure the API Key and URL are set
if not API_KEY or not API_URL:
    st.error("API_KEY or API_URL is missing! Make sure your Streamlit Cloud secrets contain them.")
    st.stop()

# Function to fetch API key (we are now using environment variable)
@st.cache_resource
def get_api_key():
    return API_KEY

# Function to communicate with the model
def chat_with_model(prompt, conversation_history=None, temperature=0.7, max_tokens=200):
    api_key = get_api_key()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "temperature": temperature,
        "max_tokens": max_tokens,
        "messages": conversation_history + [{"role": "user", "content": prompt}]
        if conversation_history else [{"role": "user", "content": prompt}]
    }
    
    response = requests.post(API_URL, headers=headers, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        assistant_message = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return assistant_message, conversation_history + [{"role": "assistant", "content": assistant_message}]
    
    # Error handling
    return f"Error: {response.status_code} - {response.text}", conversation_history

# Streamlit App
def main():
    st.set_page_config(page_title="Creysac's AI Assistant", page_icon="🤖", layout="wide")

    # Sidebar for settings
    st.sidebar.title("Settings")
    temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7, 0.05)
    max_tokens = st.sidebar.slider("Max Tokens", 1000, 128000, 5000, 200)
    #st.sidebar.caption("LLaMA 3.3 70B supports up to 128,000 tokens. Higher values allow longer responses but reduce memory for earlier context.")


    # Title
    st.title("🤖 Creysac's AI Assistant")

    BOT_NAME = "Creysac's AI"
    SYSTEM_PROMPT = f"""
    You are {BOT_NAME}, a friendly and intelligent AI chatbot built by Creysac, a person who is exploring the world of AI.
    You engage in natural conversations, provide helpful responses, and assist users with various topics.
    """

    # Initialize session state for conversation history
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = [
            {"role": "system", "content": SYSTEM_PROMPT},  # System message
            {"role": "assistant", "content": f"Hello! I am {BOT_NAME}. How can I assist you today?"}
        ]

    # Display chat history but hide the system message
    for message in st.session_state.conversation_history:
        role = message["role"]
        content = message["content"]

        if role == "system":
            continue  # Skip displaying system message

        with st.chat_message(role):
            st.markdown(f"**{role.capitalize()}**: {content}")

    # User input
    if user_input := st.chat_input("Type your message..."):
        current_time = datetime.now().strftime("%H:%M")
        
        # Append user message
        st.session_state.conversation_history.append({"role": "user", "content": user_input})
        st.chat_message("user").markdown(user_input)

        # Get bot response
        with st.spinner("Thinking..."):
            response, updated_history = chat_with_model(
                user_input,
                [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.conversation_history],
                temperature,
                max_tokens
            )

        # Append bot message
        st.session_state.conversation_history.append({"role": "assistant", "content": response})
        st.chat_message("assistant").markdown(response)

    # Clear chat history button
    if st.sidebar.button("Clear Chat History"):
        st.session_state.conversation_history = [
            {"role": "assistant", "content": "Hello! How can I assist you today?"}
        ]

if __name__ == "__main__":
    main()
