import streamlit as st
import pandas as pd
import requests
import uuid
import base64
from PIL import Image
import io

# --- PREMIUM SCREEN LAYOUT & CUSTOM STYLING ---
st.set_page_config(page_title="Quantum AI Workspace", layout="wide", initial_sidebar_state="expanded")

# Inject Premium UI and RGB Hover Effects
st.markdown("""
    <style>
    /* Premium Animated RGB Border Frame */
    .stApp {
        border: 6px solid transparent;
        border-image: linear-gradient(to right, #ff007f, #7f00ff, #00f0ff, #ff007f) 1;
        animation: premium-flow 8s linear infinite;
    }
    @keyframes premium-flow {
        0% { filter: hue-rotate(0deg); }
        100% { filter: hue-rotate(360deg); }
    }
    
    /* Elegant Welcome Overlay Card */
    .premium-welcome {
        background: linear-gradient(135deg, rgba(30, 30, 45, 0.95), rgba(15, 15, 25, 0.95));
        padding: 30px;
        border-radius: 16px;
        border: 1px solid rgba(0, 240, 255, 0.2);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 25px;
    }
    
    /* Interactive Upload Box Wrapper with Premium Hover Effect */
    div[data-testid="stFileUploader"] {
        background-color: rgba(20, 20, 35, 0.6) !important;
        border: 2px dashed rgba(127, 0, 255, 0.4) !important;
        border-radius: 12px !important;
        padding: 10px !important;
        transition: all 0.4s ease-in-out !important;
    }
    div[data-testid="stFileUploader"]:hover {
        border-color: #00f0ff !important;
        background-color: rgba(0, 240, 255, 0.05) !important;
        box-shadow: 0 0 18px rgba(0, 240, 255, 0.4) !important;
        transform: translateY(-2px);
    }
    
    /* Smooth Modern Chat Bubble Enhancements */
    .stChatMessage { border-radius: 14px; margin-bottom: 12px; padding: 16px; }
    </style>
""", unsafe_allow_html=True)

# --- WORKSPACE MEMORY ENGINE ---
if "sessions" not in st.session_state:
    st.session_state.sessions = {
        "default": {"name": "Quantum Main Session 💬", "messages": []}
    }
if "current_session" not in st.session_state:
    st.session_state.current_session = "default"

# --- SIDEBAR: HISTORICAL WORKSPACE MANAGER ---
with st.sidebar:
    st.title("⚡ Workspaces")
    if st.button("➕ Open Premium Canvas", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.sessions[new_id] = {"name": f"Session {len(st.session_state.sessions)+1}", "messages": []}
        st.session_state.current_session = new_id
        st.rerun()
        
    st.markdown("---")
    st.subheader("Active Session History")
    for session_id, session_data in list(st.session_state.sessions.items()):
        lbl = session_data["name"]
        if session_id == st.session_state.current_session:
            lbl = f"🔮 {lbl}"
        if st.button(lbl, key=f"session_{session_id}", use_container_width=True):
            st.session_state.current_session = session_id
            st.rerun()

# --- CONNECT TO DIRECT GEMINI CORE ROUTER ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("Missing API Key! Please configure GEMINI_API_KEY inside Streamlit Secrets.")
    st.stop()

def run_multimodal_brain(prompt_text, conversation_history, image_b64=None, mime_type="image/jpeg"):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    system_instruction = (
        "You are an Elite Multi-Modal System Agent. You adapt natively to all elements. "
        "If images are provided, inspect and outline them. If text sheets are uploaded, profile the data. "
        "Structure all answers inside beautiful markdown formats with neat section tabs."
    )
    
    parts_list = []
    if image_b64:
        parts_list.append({
            "inlineData": {
                "mimeType": mime_type,
                "data": image_b64
            }
        })
        
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
            return "⚠️ Data verified, but engine layout parsing failed."
    else:
        return f"🚨 API Server Connection Error ({response.status_code}): {response.text}"

# --- ACTIVE WORKSPACE COMPONENT ---
current_chat = st.session_state.sessions[st.session_state.current_session]

# Premium Welcome Interface Banner
st.markdown("""
    <div class='premium-welcome'>
        <h2 style='color:#00f0ff; margin-top:0;'>✨ Quantum Workspace Console</h2>
        <p style='color:#b0b0d0; font-size:15px; margin-bottom:0;'>
            Our premium responsive engine natively merges data indexing, contextual chat, and computer vision workflows. 
            Hover over the interface controls below to experience the responsive reactive canvas framework.
        </p>
    </div>
""", unsafe_allow_html=True)

# --- SEARCH BAR CONTROLS WITH IMAGE ICON ATTACHMENT ---
st.write("### 🔍 Premium Search Input & Image attachment Node")

col_img, col_csv = st.columns(2)
image_base64_string = None
image_mime = "image/jpeg"

with col_img:
    # This serves as the Image Icon tool container built directly into the workflow layer
    uploaded_image = st.file_uploader("🖼️ Click/Drop an image to include it in your next search prompt:", type=["png", "jpg", "jpeg"])
    if uploaded_image is not None:
        img = Image.open(uploaded_image)
        st.image(img, caption="Loaded Search Thumbnail Attachment", width=180)
        
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        image_base64_string = base64.b64encode(buffered.getvalue()).decode("utf-8")

with col_csv:
    uploaded_csv = st.file_uploader("📊 Include a CSV sheet into your search context:", type=["csv"])
    if uploaded_csv is not None:
        df = pd.read_csv(uploaded_csv)
        st.success(f"Context verified: {uploaded_csv.name}")
        st.dataframe(df.head(2), use_container_width=True)
        numeric_fields = df.select_dtypes(include=['number']).columns.tolist()
        if len(numeric_fields) >= 1:
            st.line_chart(df[numeric_fields[0]].head(15))
        csv_context = f"\n[User table resource reference: '{uploaded_csv.name}' Shape={df.shape}. Columns={numeric_fields}]"

st.markdown("---")

# Render active timeline conversations
for message in current_chat["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Text Prompt Entry Field
if user_input := st.chat_input("Enter your request here..."):
    with st.chat_message("user"):
        st.markdown(user_input)
        
    final_query = user_input + (csv_context if 'csv_context' in locals() else "")
    current_chat["messages"].append({"role": "user", "content": user_input})
    
    if len(current_chat["messages"]) == 1:
        current_chat["name"] = user_input[:20] + "..." if len(user_input) > 20 else user_input
        
    with st.chat_message("assistant"):
        with st.spinner("Processing workflows..."):
            ai_response = run_multimodal_brain(final_query, current_chat["messages"][:-1], image_base64_string, image_mime)
            st.markdown(ai_response)
            current_chat["messages"].append({"role": "assistant", "content": ai_response})
            st.rerun()