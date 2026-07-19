import streamlit as st
import pandas as pd
import requests
import uuid
import base64
from PIL import Image
import io

# --- PREMIUM PERPLEXITY-STYLE GLASSMORPHISM UI CONFIG ---
st.set_page_config(page_title="Quantum AI Search", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Premium Midnight Space Backdrop */
    .stApp {
        background-color: #0b0b10 !important;
        color: #e2e2ec !important;
    }
    
    /* Hide default Streamlit sidebar menu decorations */
    [data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* Minimalist Central Search Dashboard Header */
    .perplexity-hero {
        text-align: center;
        padding-top: 40px;
        padding-bottom: 30px;
    }
    .perplexity-hero h1 {
        font-size: 42px;
        font-weight: 700;
        letter-spacing: -1px;
        background: linear-gradient(135deg, #ffffff 30%, #ff8700 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
    }
    .perplexity-hero p {
        color: #8a8a9e;
        font-size: 16px;
    }

    /* Translucent Container Cards with Subtle Amber Hover Glow */
    .premium-panel {
        background: rgba(18, 18, 26, 0.65);
        padding: 24px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        margin-bottom: 25px;
    }
    .premium-panel:hover {
        border-color: rgba(255, 135, 0, 0.25);
        box-shadow: 0 0 30px rgba(255, 135, 0, 0.04);
        background: rgba(18, 18, 26, 0.75);
    }
    
    /* Smooth Modern Chat Turn Bubbles */
    .stChatMessage {
        border-radius: 12px;
        margin-bottom: 12px;
        border: 1px solid rgba(255, 255, 255, 0.03);
        background-color: rgba(20, 20, 30, 0.4) !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- SINGLE-PAGE APPLICATION STATE MEMORY SYSTEM ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- BACKEND API VAULT ACCESS TURN KEYS ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("Missing API Key! Please configure GEMINI_API_KEY inside Streamlit Secrets.")
    st.stop()

# --- INTELLIGENT MODEL ROUTER ENGINE TURN PIPELINES ---
def run_intelligent_intent_router(prompt_text, image_b64=None, mime_type="image/jpeg"):
    # Target standard verified endpoint configuration block
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    system_instruction = (
        "You are an Omniscient Perplexity-style AI Router and Expert Software Engineer. "
        "You automatically determine the user's intent. "
        "1. If they say 'hi' or ask simple questions, give a short, beautifully simple conversational response. "
        "2. If they ask to build, write, code, fix, or script something, output complete, production-ready, clean markdown code blocks. "
        "3. If they describe an image idea to generate art, start your response with the word '[IMAGE_GENERATION_INTENT]' "
        "followed by an expanded cinematic engineering description for an artistic master model prompt."
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
        res = requests.post(url, json=payload, headers=headers)
        if res.status_code == 200:
            return res.json()["candidates"][0]["content"]["parts"][0]["text"]
        return f"🚨 Engine Interface Error: {res.text}"
    except Exception as e:
        return f"🚨 Execution Failed: {str(e)}"

# --- IMAGEN 3 core generation engine ---
def fetch_studio_art(prompt_text):
    url = f"https://generativelanguage.googleapis.com/v1/models/imagen-3.0-generate-002:predict?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "instances": [{"prompt": prompt_text}],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "1:1",
            "outputMimeType": "image/jpeg"
        }
    }
    try:
        res = requests.post(url, json=payload, headers=headers)
        if res.status_code == 200:
            img_b64 = res.json()["predictions"][0]["bytesBase64Encoded"]
            return base64.b64decode(img_b64)
        return None
    except Exception:
        return None

# ==========================================
# --- INTENT INTERFACE DISPLAY VIEWPORTS ---
# ==========================================

# Minimalist Perplexity Heading Grid
st.markdown("""
    <div class='perplexity-hero'>
        <h1>Where knowledge begins.</h1>
        <p>Ask anything, request raw code compilation, generate art assets, or analyze data matrices instantly.</p>
    </div>
""", unsafe_allow_html=True)

# Render active dialog logs
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "visual_art_bytes" in msg:
            st.image(msg["visual_art_bytes"], caption="Generated Studio Output Canvas", use_container_width=True)
        if "attached_dataframe" in msg:
            st.dataframe(msg["attached_dataframe"], use_container_width=True)
            st.area_chart(msg["attached_dataframe"].select_dtypes(include=['number']).head(30))

st.markdown("<br><br>", unsafe_allow_html=True)

# --- INLINE EMBEDDED DUAL SYSTEM CONTROLS TRAY ---
image_base64_string = None
image_mime = "image/jpeg"
uploaded_dataframe = None

# Twin context configuration upload bars right above chat search lane row
c_upload_img, c_upload_csv = st.columns(2)

with c_upload_img:
    uploaded_img_file = st.file_uploader("🖼️ [+] Inline Image Context", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
    if uploaded_img_file is not None:
        img = Image.open(uploaded_img_file)
        st.image(img, caption="Vision Target Loaded", width=110)
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        image_base64_string = base64.b64encode(buffered.getvalue()).decode("utf-8")

with c_upload_csv:
    uploaded_csv_file = st.file_uploader("📊 [+] Inline CSV Dataset Table", type=["csv"], label_visibility="collapsed")
    if uploaded_csv_file is not None:
        uploaded_dataframe = pd.read_csv(uploaded_csv_file)
        st.success(f"Spreadsheet linked: {uploaded_csv_file.name}")

# Standard Perplexity Pill Search Input box (clears on Enter key submission instantly)
if user_query := st.chat_input("Ask anything..."):
    # Append structured dataset indicators if present
    final_query_payload = user_query
    if uploaded_dataframe is not None:
        final_query_payload += f"\n\n[User Data Attachment Content columns summary: {uploaded_dataframe.columns.tolist()}]"
        
    with st.chat_message("user"):
        st.markdown(user_query)
        
    user_log_entry = {"role": "user", "content": user_query}
    st.session_state.chat_history.append(user_log_entry)
    
    with st.chat_message("assistant"):
        with st.spinner("Searching and processing intent..."):
            ai_reply = run_intelligent_intent_router(final_query_payload, image_base64_string, image_mime)
            
            assistant_log_entry = {"role": "assistant", "content": ai_reply}
            
            # AUTOMATED INTERACTIVE INTELLIGENCE ROUTING ENGINE PATTERNS:
            # Check if text model parsed query intent to create visuals
            if "[IMAGE_GENERATION_INTENT]" in ai_reply:
                clean_prompt = ai_reply.replace("[IMAGE_GENERATION_INTENT]", "").strip()
                st.markdown(f"🎨 **Auto-Routing to Image Studio Engine:** *Generating art asset...*")
                art_bytes = fetch_studio_art(clean_prompt)
                if art_bytes:
                    st.image(art_bytes, caption="Generated Studio Output Canvas", use_container_width=True)
                    assistant_log_entry["visual_art_bytes"] = art_bytes
                    assistant_log_entry["content"] = f"🎨 Generated art based on prompt instruction blueprints:\n> {clean_prompt}"
                else:
                    st.error("Could not complete requested art creation task.")
            
            # Check if sheet file structures exist to plot dynamically
            elif uploaded_dataframe is not None:
                st.markdown(ai_reply)
                st.markdown("### 📈 Dynamic Autonomous Metric Plot")
                st.dataframe(uploaded_dataframe.head(3), use_container_width=True)
                numeric_fields = uploaded_dataframe.select_dtypes(include=['number']).columns.tolist()
                if numeric_fields:
                    st.area_chart(uploaded_dataframe[numeric_fields[0]].head(30))
                assistant_log_entry["attached_dataframe"] = uploaded_dataframe
            
            else:
                st.markdown(ai_reply)
                
            st.session_state.chat_history.append(assistant_log_entry)
            st.rerun()