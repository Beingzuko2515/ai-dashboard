import streamlit as st
import pandas as pd
import requests
import uuid
import base64
from PIL import Image
import io

# --- PREMIUM PLAIN MIDNIGHT TEXTURE WITH ORANGE MICRO-GLOW ---
st.set_page_config(page_title="Quantum AI Console", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Immersive Premium Dark Theme */
    .stApp {
        background-color: #0d0d14 !important;
        color: #e2e2ec !important;
    }
    
    /* Elegant Greeting Overlay with Premium Ambient Hover Effect */
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
        border-color: rgba(255, 135, 0, 0.3);
        background: rgba(255, 135, 0, 0.01);
        box-shadow: 0 0 20px rgba(255, 135, 0, 0.05);
    }
    
    /* Custom Styling for the Image Attachment Component */
    div[data-testid="stFileUploader"] {
        background-color: rgba(15, 15, 25, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
        padding: 6px !important;
        margin-bottom: 5px !important;
    }
    div[data-testid="stFileUploader"]:hover {
        border-color: #ff8700 !important;
    }
    
    /* Rounded Clean Chat Message Layouts */
    .stChatMessage {
        border-radius: 12px;
        margin-bottom: 10px;
        border: 1px solid rgba(255, 255, 255, 0.04);
    }
    </style>
""", unsafe_allow_html=True)

# --- WORKSPACE STATE MANAGEMENT ---
if "sessions" not in st.session_state:
    st.session_state.sessions = {
        "default": {"name": "Workspace Hub 💬", "messages": []}
    }
if "current_session" not in st.session_state:
    st.session_state.current_session = "default"

# --- SIDEBAR WORKSPACE CANVAS SELECTOR ---
with st.sidebar:
    st.title("🔮 Core Hub")
    if st.button("➕ New Workspace Canvas", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.sessions[new_id] = {"name": f"Session {len(st.session_state.sessions)+1}", "messages": []}
        st.session_state.current_session = new_id
        st.rerun()
        
    st.markdown("---")
    st.caption("SAVED WORKSPACES")
    for session_id, session_data in list(st.session_state.sessions.items()):
        lbl = session_data["name"]
        if session_id == st.session_state.current_session:
            lbl = f"🔸 {lbl}"
        if st.button(lbl, key=f"session_{session_id}", use_container_width=True):
            st.session_state.current_session = session_id
            st.rerun()

# --- BACKEND MULTIMODAL GEMINI GATEWAY ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("Missing API Key! Please configure GEMINI_API_KEY inside Streamlit Secrets.")
    st.stop()

def run_multimodal_brain(prompt_text, conversation_history, image_b64=None, mime_type="image/jpeg"):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    system_instruction = (
        "You are a helpful, simple, friendly, and powerful AI Assistant and Expert Code Generator. "
        "When the user greets you with basic statements like 'hi', answer with a short, friendly greeting. "
        "When requested to create scripts, programs, or fix code blocks, provide clean, functional, production-ready code."
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
            return "⚠️ System parsed conversation turn, but response format layout was corrupted."
    else:
        return f"🚨 API Engine Error ({response.status_code}): {response.text}"

# --- PRIMARY WORKSPACE FRAME VIEWPORT ---
current_chat = st.session_state.sessions[st.session_state.current_session]

st.markdown("""
    <div class='premium-card'>
        <h3 style='color:#ff8700; margin-top:0;'>✨ Quantum Workspace Console</h3>
        <p style='color:#9e9eaf; font-size:14px; margin-bottom:0;'>
            Type your messages and press <b>Enter</b> to instantly converse or generate code. Use the micro media block right above the input bar to attach visual targets seamlessly.
        </p>
    </div>
""", unsafe_allow_html=True)

# Stream historical dialog logs
for message in current_chat["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- INTEGRATED DUAL SEARCH & INPUT CONTROLS ---
image_base64_string = None
image_mime = "image/jpeg"

# Minimalist Media Drop Anchor placed perfectly right above the input row
uploaded_image = st.file_uploader("➕ Add Image Context to Search", type=["png", "jpg", "jpeg"], key="embedded_search_uploader")
if uploaded_image is not None:
    img = Image.open(uploaded_image)
    st.image(img, caption="Active Media Element Verified", width=120)
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    image_base64_string = base64.b64encode(buffered.getvalue()).decode("utf-8")

# Native input bar fixes: Auto-clears input, allows direct keyboard execution on Enter keypress
if user_input := st.chat_input("Ask anything, generate code, or analyze image targets..."):
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