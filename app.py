import streamlit as st
import pandas as pd
import requests
import uuid
import base64
from PIL import Image
import io

# --- DEEP PREMIUM DARK CONFIG & PREMIUM AMBIENT ORANGE HOVER ---
st.set_page_config(page_title="Quantum AI Workspace", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Immersive Dark Theme background */
    .stApp {
        background-color: #0d0d14 !important;
        color: #e2e2ec !important;
    }
    
    /* Welcome banner card with sleek orange glow border on hover */
    .premium-card {
        background: rgba(20, 20, 30, 0.7);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease-in-out;
        margin-bottom: 20px;
    }
    .premium-card:hover {
        border-color: rgba(255, 135, 0, 0.4);
        background: rgba(255, 135, 0, 0.01);
        box-shadow: 0 0 20px rgba(255, 135, 0, 0.06);
    }
    
    /* Interactive file attachment input dropzone with active orange focus highlights */
    div[data-testid="stFileUploader"] {
        background-color: rgba(15, 15, 25, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        padding: 4px !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stFileUploader"]:hover {
        border-color: #ff8700 !important;
        box-shadow: 0 0 12px rgba(255, 135, 0, 0.15) !important;
    }
    
    /* Modern message bubble containers */
    .stChatMessage {
        border-radius: 12px;
        margin-bottom: 10px;
        border: 1px solid rgba(255, 255, 255, 0.04);
    }
    </style>
""", unsafe_allow_html=True)

# --- CHAT SESSION MANAGEMENT FRAMEWORK ---
if "sessions" not in st.session_state:
    st.session_state.sessions = {
        "default": {"name": "Workspace Main 💬", "messages": []}
    }
if "current_session" not in st.session_state:
    st.session_state.current_session = "default"

# --- SIDEBAR navigation panels ---
with st.sidebar:
    st.title("🔮 Core Hub")
    if st.button("➕ New Workspace Canvas", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.sessions[new_id] = {"name": f"Session {len(st.session_state.sessions)+1}", "messages": []}
        st.session_state.current_session = new_id
        st.rerun()
        
    st.markdown("---")
    st.caption("SAVED CHATS")
    for session_id, session_data in list(st.session_state.sessions.items()):
        lbl = session_data["name"]
        if session_id == st.session_state.current_session:
            lbl = f"🔸 {lbl}"
        if st.button(lbl, key=f"session_{session_id}", use_container_width=True):
            st.session_state.current_session = session_id
            st.rerun()

# --- BACKEND API ACCESS PROTOCOLS ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("Missing API Key! Please configure GEMINI_API_KEY inside Streamlit Secrets.")
    st.stop()

def run_multimodal_brain(prompt_text, conversation_history, image_b64=None, mime_type="image/jpeg"):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    # Restructured Instruction Set: Keeps replies simple/casual for greetings, but lets it act as an elite coding engine on request.
    system_instruction = (
        "You are a helpful, simple, and powerful AI Assistant and Coding Expert. "
        "When the user greets you normally (like 'hi' or 'hello'), reply conversationally, simply and directly "
        "without drawing large system capability tables or matrices unless explicitly asked. "
        "If they ask you to write code, program apps, analyze files, or fix bugs, become an expert software engineer "
        "and provide fully functioning, clear, production-ready code blocks inside markdown styling."
    )
    
    parts_list = []
    if image_b64:
        parts_list.append({"inlineData": {"mimeType": mime_type, "data": image_b64}})
        
    parts_list.append({"text": prompt_text})
    
    payload = {
        "contents": [{"role": "user", "parts": parts_list}],
        "systemInstruction": {"parts": [{"text": system_instruction}]}
    }
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        try:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            return "⚠️ System parsed message, but response format structure was corrupted."
    else:
        return f"🚨 API Connection Error ({response.status_code}): {response.text}"

# --- APP LAYOUT RENDERING VIEWPORTS ---
current_chat = st.session_state.sessions[st.session_state.current_session]

st.markdown("""
    <div class='premium-card'>
        <h3 style='color:#ff8700; margin-top:0;'>✨ Quantum Workspace Console</h3>
        <p style='color:#9e9eaf; font-size:14px; margin-bottom:0;'>
            Ask questions, attach files, or generate programs instantly. The unified engine processes standard queries and advanced script coding seamlessly.
        </p>
    </div>
""", unsafe_allow_html=True)

# Render conversation logs
for message in current_chat["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

st.markdown("---")

# --- UNIFIED INLINE UTILITY BOTTOM ROW ---
image_base64_string = None
image_mime = "image/jpeg"

col_btn, col_txt = st.columns([1, 4])

with col_btn:
    # Minimal input image upload element placed completely inline right beside search line rows
    uploaded_image = st.file_uploader("🖼️ [+] Add Media", type=["png", "jpg", "jpeg"], key="inline_media_uploader", label_visibility="collapsed")
    if uploaded_image is not None:
        img = Image.open(uploaded_image)
        st.image(img, caption="Image Active", width=90)
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        image_base64_string = base64.b64encode(buffered.getvalue()).decode("utf-8")

with col_txt:
    # Streamlined interactive text field block input mapping tools
    user_input = st.text_input("Message the AI or type code requests...", placeholder="Say hi, ask for a Python script, or pass media instructions...", key="inline_search_query", label_visibility="collapsed")
    submit_action = st.button("Send Query 🚀", use_container_width=True)

# Processing logic execution pipeline
if submit_action and user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
        
    current_chat["messages"].append({"role": "user", "content": user_input})
    
    if len(current_chat["messages"]) == 1:
        current_chat["name"] = user_input[:20] + "..." if len(user_input) > 20 else user_input
        
    with st.chat_message("assistant"):
        with st.spinner("Processing request..."):
            ai_response = run_multimodal_brain(user_input, current_chat["messages"][:-1], image_base64_string, image_mime)
            st.markdown(ai_response)
            current_chat["messages"].append({"role": "assistant", "content": ai_response})
            st.rerun()