import streamlit as st
import pandas as pd
import requests
import json
import uuid

# --- GLOBAL CONFIGURATION & STYLING ---
st.set_page_config(page_title="AI Hyper-Agent Workspace", layout="wide", initial_sidebar_state="expanded")

# Inject custom CSS for a cleaner, modern chat interface and better contrast accessibility
st.markdown("""
    <style>
    .stChatMessage { border-radius: 12px; margin-bottom: 10px; padding: 15px; }
    .stChatInputContainer { border-top: 1px solid #ccc; padding-top: 10px; }
    button[kind="secondary"] { border-radius: 20px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- INITIALIZE CHAT HISTORY STORAGE ---
if "sessions" not in st.session_state:
    st.session_state.sessions = {
        "default": {"name": "New Chat Workspace ✨", "messages": []}
    }
if "current_session" not in st.session_state:
    st.session_state.current_session = "default"

# --- SIDEBAR: PERSISTENT CONVERSATION HISTORY (Like ChatGPT/Gemini) ---
with st.sidebar:
    st.title("🗂️ Chat Workspaces")
    
    # Button to launch a clean new session
    if st.button("➕ Start New Chat", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.sessions[new_id] = {"name": f"Chat session {len(st.session_state.sessions) + 1}", "messages": []}
        st.session_state.current_session = new_id
        st.rerun()
        
    st.markdown("---")
    st.subheader("Recent Sessions")
    
    # List all historic saved sessions dynamically
    for session_id, session_data in list(st.session_state.sessions.items()):
        button_label = session_data["name"]
        # Highlight active session visually
        if session_id == st.session_state.current_session:
            button_label = f"▶️ {button_label}"
            
        if st.button(button_label, key=f"session_{session_id}", use_container_width=True):
            st.session_state.current_session = session_id
            st.rerun()

# --- MAIN ENGINE: DIRECT API CALL WITH AGENT TOOLS ROUTER ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("API Key missing! Please make sure GEMINI_API_KEY is configured in your Streamlit Secrets.")
    st.stop()

def run_agent_brain(prompt_text, conversation_history):
    # Using the current standard free-tier model string
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    # Format current dynamic history + system system prompt routing capabilities
    system_instruction = (
        "You are an Omni-Tool Intelligent Agent. You autonomously decide how to handle user intents. "
        "If a user wants structural outlines, data blueprints, or creative generation instructions, "
        "always organize it beautifully using Markdown tables, headers, and bullet structures. "
        "Provide direct actionable instructions cleanly."
    )
    
    # Compile history cleanly for structural payload delivery
    formatted_contents = []
    for msg in conversation_history[-6:]: # Pass the last 3 turns for context stability
        role_label = "user" if msg["role"] == "user" else "model"
        formatted_contents.append({"role": role_label, "parts": [{"text": msg["content"]}]})
        
    # Append fresh query request
    formatted_contents.append({"role": "user", "parts": [{"text": prompt_text}]})
    
    payload = {
        "contents": formatted_contents,
        "systemInstruction": {"parts": [{"text": system_instruction}]}
    }
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        try:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            return "⚠️ Connection verified, but response structural mapping failed."
    else:
        return f"🚨 API Server Connection Error ({response.status_code}): {response.text}"

# --- ACTIVE WORKSPACE INTERFACE ---
current_chat = st.session_state.sessions[st.session_state.current_session]

st.title("🤖 Intelligent Multi-Tool Workspace")
st.write(f"Active Workspace: **{current_chat['name']}**")
st.caption("Type naturally! The system automatically detects data analytics, text processing, or visual concept generation rules.")

# --- PERSISTENT UTILITY UPLOADER RIGHT INSIDE CHAT WORKSPACE ---
with st.expander("📎 Click here to attach CSV spreadsheets or Data Reports for the AI to inspect", expanded=False):
    uploaded_file = st.file_uploader("Drop your dataset here:", type=["csv", "txt"])
    if uploaded_file is not None:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
            st.success(f"Successfully loaded data matrix: '{uploaded_file.name}'")
            
            # Context splits into visual chart widgets automatically inside workflow window
            c1, c2 = st.columns(2)
            with c1:
                st.write("**Data Insight Frame Preview:**")
                st.dataframe(df.head(3))
            with c2:
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                if len(numeric_cols) >= 1:
                    target_col = st.selectbox("Select column to graph instantly:", numeric_cols)
                    st.line_chart(df[target_col].head(20))
            
            # Silently append data structure overview to chat environment context window
            data_summary = f"\n[User has attached file table: '{uploaded_file.name}'. Summary: Shape={df.shape}, Numeric fields={numeric_cols}]"
        else:
            data_summary = f"\n[User text document upload content follows:\n{uploaded_file.getvalue().decode('utf-8')[:2000]}]"

# Render active window messages history frame
for message in current_chat["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input Execution Layer
if user_query := st.chat_input("Ask a question, request a script, or issue analysis commands..."):
    # Append visual input context to screen space
    with st.chat_message("user"):
        st.markdown(user_query)
        
    # Inject extra file variables data context safely if exist
    injected_query = user_query + (data_summary if 'data_summary' in locals() else "")
    current_chat["messages"].append({"role": "user", "content": user_query})
    
    # Auto rename default chat dynamically based on initial entry
    if len(current_chat["messages"]) == 1:
        current_chat["name"] = user_query[:25] + "..." if len(user_query) > 25 else user_query
        
    # Execute autonomous output pipeline
    with st.chat_message("assistant"):
        with st.spinner("Processing workflows..."):
            ai_output = run_agent_brain(injected_query, current_chat["messages"][:-1])
            st.markdown(ai_output)
            current_chat["messages"].append({"role": "assistant", "content": ai_output})
            st.rerun()