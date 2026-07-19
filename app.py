import streamlit as st
import pandas as pd
from google import genai

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Universal AI Agent Dashboard", layout="wide")
st.title("🤖 Universal AI Agent Dashboard")
st.write("Your central hub for problem-solving and automated tools.")

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["💬 AI Agent Chat", "📊 Data Analyst Tool"])

# --- FETCH SECRET API KEY ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except Exception:
    st.error("API Key missing! Please set up your Streamlit Secrets.")
    st.stop()

# --- PAGE 1: AI AGENT CHAT ---
if page == "💬 AI Agent Chat":
    st.header("💬 Talk to your AI Agent")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What problem can I solve for you today?"):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            
            # Using the updated gemini-3.5-flash model
            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=prompt,
            )
            
            ai_response = response.text
            response_placeholder.markdown(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})

# --- PAGE 2: DATA ANALYST TOOL ---
elif page == "📊 Data Analyst Tool":
    st.header("📊 AI Data Analyst")
    st.write("Upload a CSV file to check out your data metrics.")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df.head())