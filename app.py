import streamlit as st
import pandas as pd
import requests
import uuid
import base64
from PIL import Image
import io

# --- DEEP MIDNIGHT DARK MODE CONFIG & GEMINI PILL BAR CSS ---
st.set_page_config(page_title="Quantum AI Console", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Immersive Dark Theme background */
    .stApp {
        background-color: #0d0d14 !important;
        color: #e2e2ec !important;
    }
    
    /* Welcome card layout containing a premium amber glow hover matrix */
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
    
    /* --- ULTRACLEAN INTEGRATED PILL DESIGN PACK --- */
    /* Stripping down the upload container to form an embedded '+' icon node */
    div[data-testid="stFileUploader"] {
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin-top: 4px !important;
    }
    div[data-testid="stFileUploader"] section {
        padding: 0 !important;
        border: none !important;
        background: transparent !important;
    }
    /* Stylizing the upload trigger label into a clean interactive element link */
    div[data-testid="stFileUploader"] label {
        display: none !important;
    }
    
    /* Clean chat message layout panels */
    .stChatMessage {
        border-radius: 12px;
        margin-bottom: 10px;
        border: 1px solid rgba(255, 255, 255, 0.04);
    }
    
    /* Soft glowing style for the execution action link */
    .submit-pill-btn button {
        background-color: #ff8700 !important;
        color: white !important;
        border-radius: 20px !important;
        border: none !important;
        font-weight: bold !important;
        transition: all 0.2s !important;
    }
    .submit-pill-btn button:hover {
        box-shadow: 0 0 12px rgba(255, 135, 0, 0.5) !important;
        transform: scale(1.02);
    }
    </style>
""", unsafe_allow_html=True)

# --- CHAT WORKSPACE STORAGE SYSTEMS ---
if "sessions" not in st.session_state:
    st.session_state.sessions = {
        "default": {"name": "Workspace Main 💬", "messages": []}
    }
if "current_session" not in st.session_state:
    st.session_state.current_session = "default"

# --- SIDEBAR DRAWER MANAGER ---
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

# --- BACKEND MULTIMODAL API ROUTER ENGINE ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("Missing API Key! Please configure GEMINI_API_KEY inside Streamlit Secrets.")
    st.stop()

def run_multimodal_brain(prompt_text, conversation_history, image_b64=None, mime_type="image/jpeg"):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    system_instruction = (
        "You are a helpful, direct, and powerful AI Assistant and Coding Expert. "
        "Keep greeting responses simple, short, and friendly (e.g., 'Hello! How can I help you today?'). "
        "When asked to write code, provide clean, efficient, functional code blocks inside standard markdown syntax."
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

# --- PRIMARY DISPLAY FRAME ---
current_chat = st.session_state.sessions[st.session_state.current_session]

st.markdown("""
    <div class='premium-card'>
        <h3 style='color:#ff8700; margin-top:0;'>✨ Quantum Workspace</h3>
        <p style='color:#9e9eaf; font-size:14px; margin-bottom:0;'>
            Seamless Gemini UI Console. Use the clean media capsule embedded inside the search layout bar below to run code generation and computer vision queries.
        </p>
    </div>
""", unsafe_allow_html=True)

# Render conversation logs
for message in current_chat["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

st.markdown("---")

# --- CUSTOM PILL SEARCH BAR INCORPORATING EMBEDDED '+' ICON ---
image_base64_string = None
image_mime = "image/jpeg"

# Using unified layout columns with minimal gaps to mock a singular interactive capsule entry row
col_plus_icon, col_input_field, col_submit_btn = st.columns([0.4, 4.8, 0.8])

with col_plus_icon:
    # Minimal text label heading acts as the structural alignment anchor for the inline file stream clicker
    st.caption("➕ Attachment")
    uploaded_image = st.file_uploader("Upload", type=["png", "jpg", "jpeg"], key="gemini_style_icon_uploader", label_visibility="collapsed")
    if uploaded_image is not None:
        img = Image.open(uploaded_image)
        # Visual clip tag showing file state below the bar frame
        st.image(img, caption="Media Loaded ✅", width=55)
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        image_base64_string = base64.b64encode(buffered.getvalue()).decode("utf-8")

with col_input_field:
    user_input = st.text_input(
        "Ask Gemini...", 
        placeholder="Ask a question, request code generation, or query attached visual elements...", 
        key="gemini_search_bar_string",
        label_visibility="collapsed"
    )

with col_submit_btn:
    st.markdown('<div class="submit-pill-btn">', unsafe_allow_html=True)
    submit_action = st.button("Send 🚀", use_container_width=True, key="pill_action_fire")
    st.markdown('</div>', unsafe_allow_html=True)

# Processing logic pipeline
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