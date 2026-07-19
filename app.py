import streamlit as st
import pandas as pd
import requests
import uuid
import base64
from PIL import Image
import io

# --- PREMIUM MIDNIGHT DARK MODE WITH AMBIENT ORANGE ACCENTS ---
st.set_page_config(page_title="Global AI Dashboard", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Premium Deep Dark Theme */
    .stApp {
        background-color: #0d0d14 !important;
        color: #e2e2ec !important;
    }
    
    /* Clean feature info card with glowing hover effect */
    .feature-card {
        background: rgba(20, 20, 30, 0.7);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease-in-out;
        margin-bottom: 20px;
    }
    .feature-card:hover {
        border-color: rgba(255, 135, 0, 0.3);
        background: rgba(255, 135, 0, 0.01);
        box-shadow: 0 0 20px rgba(255, 135, 0, 0.05);
    }
    
    /* Unified file picker custom border styles */
    div[data-testid="stFileUploader"] {
        background-color: rgba(15, 15, 25, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
        padding: 6px !important;
    }
    div[data-testid="stFileUploader"]:hover {
        border-color: #ff8700 !important;
    }
    
    /* Smooth modern chat chat logs layout frames */
    .stChatMessage {
        border-radius: 12px;
        margin-bottom: 10px;
        border: 1px solid rgba(255, 255, 255, 0.04);
    }
    </style>
""", unsafe_allow_html=True)

# --- APP CONFIGURATION & STATE ROUTING ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- MULTI-FEATURE ROUTER SIDEBAR ---
with st.sidebar:
    st.title("🚀 Navigation Menu")
    st.caption("GO TO FEATURE:")
    feature = st.radio(
        "Select Workflow", 
        ["💬 AI Agent Chat & Code Gen", "🖼️ AI Art Concept Generator", "📊 Advanced Data Analyst"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    if st.button("🗑️ Clear Active History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- CONNECT SECURELY TO THE LATEST GEMINI CORE ROUTER ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("Missing API Key! Please configure GEMINI_API_KEY inside Streamlit Secrets.")
    st.stop()

def run_gemini_core(prompt_text, image_b64=None, mime_type="image/jpeg"):
    # Target standard verified stable deployment model endpoint 
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    system_instruction = (
        "You are a helpful, simple, friendly AI Assistant and Expert Code Generator. "
        "Keep normal conversational greetings short and clean (e.g. 'Hello! How can I help you today?'). "
        "When asked to write code, provide fully functional, clean, well-commented code blocks inside standard markdown blocks."
    )
    
    parts_list = []
    if image_b64:
        parts_list.append({"inlineData": {"mimeType": mime_type, "data": image_b64}})
    parts_list.append({"text": prompt_text})
    
    payload = {
        "contents": [{"role": "user", "parts": parts_list}],
        "systemInstruction": {"parts": [{"text": system_instruction}]}
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"🚨 API Connection Error (Status Code: {response.status_code}). Check your project billing/secrets."
    except Exception as e:
        return f"🚨 Connection Failed: {str(e)}"

# --- WORKSPACE DASHBOARD VIEWPORTS ---
if feature == "💬 AI Agent Chat & Code Gen":
    st.markdown("""
        <div class='feature-card'>
            <h2 style='color:#ff8700; margin-top:0;'>💬 AI Agent Chat & Code Generator</h2>
            <p style='color:#9e9eaf; font-size:14px; margin-bottom:0;'>
                Type your request and press <b>Enter</b> to talk or generate programs instantly. Use the optional media clip directly below to include vision context.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Display message history streams
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Inline Media Tray Component completely cleared of broken frameworks
    image_base64_string = None
    image_mime = "image/jpeg"
    uploaded_file = st.file_uploader("➕ Attach optional image context to search:", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        st.image(img, caption="Media context linked", width=120)
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        image_base64_string = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
    st.markdown("---")
    
    # Native Chat Input component automatically triggers on Enter and clears out old inputs instantly
    if user_input := st.chat_input("Ask me anything or ask me to write a script..."):
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.chat_message("assistant"):
            with st.spinner("Processing framework query..."):
                response_text = run_gemini_core(user_input, image_base64_string, image_mime)
                st.markdown(response_text)
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        st.rerun()

elif feature == "🖼️ AI Art Concept Generator":
    st.markdown("""
        <div class='feature-card'>
            <h2 style='color:#ff8700; margin-top:0;'>🖼️ AI Art Concept Generator</h2>
            <p style='color:#9e9eaf; font-size:14px; margin-bottom:0;'>
                Describe the image concept you want to create below. The AI will engineer a comprehensive prompt layout structure for you.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    art_prompt = st.text_input("Enter creative script prompt:", placeholder="e.g. A futuristic city at sunset...")
    if st.button("Generate Layout Prompt ✨"):
        if art_prompt:
            with st.spinner("Engineering creative prompt blueprint..."):
                structured_query = f"Provide a highly descriptive, visually descriptive prompt layout for a digital artist based on: {art_prompt}"
                art_response = run_gemini_core(structured_query)
                st.info(art_response)
        else:
            st.warning("Please enter a description text prompt first!")

elif feature == "📊 Advanced Data Analyst":
    st.markdown("""
        <div class='feature-card'>
            <h2 style='color:#ff8700; margin-top:0;'>📊 Advanced Data Analyst</h2>
            <p style='color:#9e9eaf; font-size:14px; margin-bottom:0;'>
                Drop a structural data layout spreadsheet here to extract information summaries instantly.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    data_file = st.file_uploader("Upload spreadsheet data context:", type=["csv"])
    if data_file is not None:
        df = pd.read_csv(data_file)
        st.success("Matrix successfully parsed!")
        st.dataframe(df.head(5), use_container_width=True)
        
        if st.button("Analyze Sheet Metrics 📈"):
            with st.spinner("Calculating data insights..."):
                analytics_query = f"Summarize the structural intent of a table dataset containing these columns: {df.columns.tolist()}"
                analytics_response = run_gemini_core(analytics_query)
                st.markdown(analytics_response)