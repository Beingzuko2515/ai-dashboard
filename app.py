import streamlit as st
import pandas as pd
import requests
import uuid
import base64
from PIL import Image
import io

# --- DEEP PREMIUM DARK CONFIG & CUSTOM INTERACTIVE CSS ---
st.set_page_config(page_title="Quantum AI Console", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Premium Immersive Midnight Backdrop */
    .stApp {
        background-color: #0d0d14 !important;
        color: #e2e2ec !important;
    }
    
    /* Clean Ambient Card with Orange Glow on Hover */
    .premium-card {
        background: rgba(20, 20, 30, 0.7);
        padding: 24px;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
        transition: all 0.4s ease-in-out;
        margin-bottom: 25px;
    }
    .premium-card:hover {
        border-color: rgba(255, 135, 0, 0.4);
        background: rgba(255, 135, 0, 0.02);
        box-shadow: 0 0 25px rgba(255, 135, 0, 0.08);
    }
    
    /* Sleek Orange Glow Customization for File Drop Zones */
    div[data-testid="stFileUploader"] {
        background-color: rgba(15, 15, 25, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        padding: 8px !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="stFileUploader"]:hover {
        border-color: #ff8700 !important;
        box-shadow: 0 0 15px rgba(255, 135, 0, 0.15) !important;
    }
    
    /* Modernized Chat Bubbles */
    .stChatMessage {
        border-radius: 12px;
        margin-bottom: 10px;
        border: 1px solid rgba(255, 255, 255, 0.04);
    }
    </style>
""", unsafe_allow_html=True)

# --- WORKSPACE MEMORY SYSTEM ---
if "sessions" not in st.session_state:
    st.session_state.sessions = {
        "default": {"name": "Workspace Hub 💬", "messages": []}
    }
if "current_session" not in st.session_state:
    st.session_state.current_session = "default"

# --- SIDEBAR: CLEAN STREAMLINED CONVERSATION DRAWER ---
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

# --- CONNECT TO STABLE API DIRECT ROUTER ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("Missing API Key! Please configure GEMINI_API_KEY inside Streamlit Secrets.")
    st.stop()

def run_multimodal_brain(prompt_text, conversation_history, image_b64=None, mime_type="image/jpeg"):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    system_instruction = (
        "You are an Elite Intelligence System Agent. You adapt smoothly to multimodal inputs. "
        "Provide direct actionable instructions cleanly using rich Markdown tables and bullet grids."
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
            return "⚠️ System parsed message, but response structure was corrupted."
    else:
        return f"🚨 API Server Connection Error ({response.status_code}): {response.text}"

# --- ACTIVE WORKSPACE COMPONENT ---
current_chat = st.session_state.sessions[st.session_state.current_session]

# Interactive Premium Welcome Card
st.markdown("""
    <div class='premium-card'>
        <h3 style='color:#ff8700; margin-top:0;'>✨ Quantum Workspace</h3>
        <p style='color:#9e9eaf; font-size:14px; margin-bottom:0;'>
            Experience an autonomous multi-modal sandbox. Use the streamlined context tray above the input line to attach media dynamically.
        </p>
    </div>
""", unsafe_allow_html=True)

# Render historical dialogue cards
for message in current_chat["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- THE INTEGRATED BOTTOM SEARCH INPUT & TRAY INTERFACE ---
st.markdown("---")

image_base64_string = None
image_mime = "image/jpeg"
csv_context = ""

# Minimalist integrated drawer toggle right above input text area
with st.expander("➕ Add Media Attachment Context to Input Search", expanded=False):
    col_media_img, col_media_data = st.columns(2)
    with col_media_img:
        uploaded_image = st.file_uploader("🖼️ Attach Image to Query Input Node:", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
        if uploaded_image is not None:
            img = Image.open(uploaded_image)
            st.image(img, caption="Media Slot Active", width=140)
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG")
            image_base64_string = base64.b64encode(buffered.getvalue()).decode("utf-8")
            
    with col_media_data:
        uploaded_csv = st.file_uploader("📊 Attach CSV Sheet Reference:", type=["csv"], label_visibility="collapsed")
        if uploaded_csv is not None:
            df = pd.read_csv(uploaded_csv)
            st.success(f"Linked data matrix: {uploaded_csv.name}")
            st.dataframe(df.head(1), use_container_width=True)
            numeric_fields = df.select_dtypes(include=['number']).columns.tolist()
            if len(numeric_fields) >= 1:
                st.line_chart(df[numeric_fields[0]].head(10))
            csv_context = f"\n[User Data Attachment Content: '{uploaded_csv.name}' Columns={numeric_fields}]"

# Clean Text Entry Prompt Bar
if user_input := st.chat_input("Ask a question, analyze data, or map concepts..."):
    with st.chat_message("user"):
        st.markdown(user_input)
        
    final_query = user_input + csv_context
    current_chat["messages"].append({"role": "user", "content": user_input})
    
    if len(current_chat["messages"]) == 1:
        current_chat["name"] = user_input[:20] + "..." if len(user_input) > 20 else user_input
        
    with st.chat_message("assistant"):
        with st.spinner("Executing query matrix..."):
            ai_response = run_multimodal_brain(final_query, current_chat["messages"][:-1], image_base64_string, image_mime)
            st.markdown(ai_response)
            current_chat["messages"].append({"role": "assistant", "content": ai_response})
            st.rerun()