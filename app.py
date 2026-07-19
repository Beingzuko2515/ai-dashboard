import streamlit as st
import pandas as pd
import requests
import uuid
import base64
from PIL import Image
import io

# --- APP CONFIGURATION & DYNAMIC ANIMATED RGB BORDER ---
st.set_page_config(page_title="Omni-Agent Hub", layout="wide", initial_sidebar_state="expanded")

# Inject CSS for an awesome animated RGB glowing frame and accessible typography
st.markdown("""
    <style>
    /* Animated RGB Border Frame around the entire app window */
    .stApp {
        border: 8px solid transparent;
        border-image: linear-gradient(to bottom right, #ff007f, #7f00ff, #00f0ff, #ff007f) 1;
        animation: rgb-glow 6s linear infinite;
    }
    @keyframes rgb-glow {
        0% { filter: hue-rotate(0deg); }
        100% { filter: hue-rotate(360deg); }
    }
    
    /* Clean welcome message styling */
    .welcome-card {
        background: linear-gradient(135deg, rgba(127,0,255,0.1), rgba(0,240,255,0.05));
        padding: 25px;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.15);
        margin-bottom: 20px;
    }
    
    .stChatMessage { border-radius: 12px; margin-bottom: 12px; padding: 14px; }
    </style>
""", unsafe_allow_html=True)

# --- TRACK SESSION HISTORY SYSTEM ---
if "sessions" not in st.session_state:
    st.session_state.sessions = {
        "default": {"name": "Main Chat Hub 💬", "messages": []}
    }
if "current_session" not in st.session_state:
    st.session_state.current_session = "default"

# --- SIDEBAR SESSION DRAWER ---
with st.sidebar:
    st.title("🗂️ Chat Workspaces")
    if st.button("➕ Start New Chat", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.sessions[new_id] = {"name": f"Session {len(st.session_state.sessions)+1}", "messages": []}
        st.session_state.current_session = new_id
        st.rerun()
        
    st.markdown("---")
    st.subheader("Saved Chats")
    for session_id, session_data in list(st.session_state.sessions.items()):
        lbl = session_data["name"]
        if session_id == st.session_state.current_session:
            lbl = f"▶️ {lbl}"
        if st.button(lbl, key=f"session_{session_id}", use_container_width=True):
            st.session_state.current_session = session_id
            st.rerun()

# --- CONNECT TO GEMINI API DIRECT ENGINE ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("Missing API Key! Please configure GEMINI_API_KEY inside Streamlit Secrets.")
    st.stop()

def run_multimodal_brain(prompt_text, conversation_history, image_b64=None, mime_type="image/jpeg"):
    # Target endpoint for gemini-3.5-flash
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    system_instruction = (
        "You are an Omni-Tool Intelligence Engine. You automatically identify the user's intent. "
        "If they give you data frames/CSV shapes, run analysis. If they attach images, detail them. "
        "If they request art templates, draw an expansive architectural Markdown layout blueprint for concepts. "
        "Always structure insights gracefully using tables, bolds, and list grids."
    )
    
    # Bundle text thread history turns safely
    parts_list = []
    
    # Incorporate Image attachment inside payload if provided
    if image_b64:
        parts_list.append({
            "inlineData": {
                "mimeType": mime_type,
                "data": image_b64
            }
        })
        
    # Append actual prompt request text
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
            return "⚠️ Server connection active, but could not parse the response data structure."
    else:
        return f"🚨 API Server Connection Error ({response.status_code}): {response.text}"

# --- CORE USER INTERFACE CANVAS ---
current_chat = st.session_state.sessions[st.session_state.current_session]

# Header Showcase Message Banner
st.markdown("""
    <div class='welcome-card'>
        <h2>✨ Welcome to the Intelligent Super-Agent Suite</h2>
        <p>Type queries freely! Drop images to analyze them, upload data sheets to graph them, or brainstorm code out loud. The underlying pipeline automatically routes actions based on your input parameters.</p>
    </div>
""", unsafe_allow_html=True)

# --- MODERN IN-LINE MULTIMEDIA SEARCH & UPLOAD BOX ---
st.write("### 🔍 Omni Search & Media Attachment Input")
col_upload, col_data = st.columns(2)

image_base64_string = None
image_mime = "image/jpeg"

with col_upload:
    uploaded_image = st.file_uploader("🖼️ Attach image here to query visual elements:", type=["png", "jpg", "jpeg"])
    if uploaded_image is not None:
        # Open and show file element
        img = Image.open(uploaded_image)
        st.image(img, caption="Loaded Input Target", width=220)
        
        # Parse into standard transmission payload bytes
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        image_base64_string = base64.b64encode(buffered.getvalue()).decode("utf-8")
        image_mime = "image/jpeg"

with col_data:
    uploaded_csv = st.file_uploader("📊 Drop a dataset CSV file here to chart numeric rows:", type=["csv"])
    if uploaded_csv is not None:
        df = pd.read_csv(uploaded_csv)
        st.success(f"Loaded matrix layout: {uploaded_csv.name}")
        st.dataframe(df.head(2), use_container_width=True)
        numeric_fields = df.select_dtypes(include=['number']).columns.tolist()
        if len(numeric_fields) >= 1:
            st.line_chart(df[numeric_fields[0]].head(15))
        csv_context = f"\n[Data reference attached: '{uploaded_csv.name}' Shape info: {df.shape}. Numeric variables: {numeric_fields}]"

st.markdown("---")

# Render active timeline conversation messages 
for message in current_chat["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Text Query Execution Strip
if user_input := st.chat_input("Write a prompt, request an art template layout, or analyze visual contexts..."):
    with st.chat_message("user"):
        st.markdown(user_input)
        
    # Append spreadsheet contexts to text string seamlessly if active
    final_query = user_input + (csv_context if 'csv_context' in locals() else "")
    current_chat["messages"].append({"role": "user", "content": user_input})
    
    # Auto adjust session label name dynamically
    if len(current_chat["messages"]) == 1:
        current_chat["name"] = user_input[:20] + "..." if len(user_input) > 20 else user_input
        
    with st.chat_message("assistant"):
        with st.spinner("Analyzing parameters autonomously..."):
            ai_response = run_multimodal_brain(final_query, current_chat["messages"][:-1], image_base64_string, image_mime)
            st.markdown(ai_response)
            current_chat["messages"].append({"role": "assistant", "content": ai_response})
            st.rerun()