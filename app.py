import streamlit as st
import pandas as pd
import requests
import uuid
import base64
from PIL import Image
import io

# --- PREMIUM HOVER-GLOW PERPLEXITY UI LAYOUT ---
st.set_page_config(page_title="Perplexity AI Console", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Premium Midnight Backdrop */
    .stApp {
        background-color: #0b0b10 !important;
        color: #e2e2ec !important;
    }
    
    /* Remove default Streamlit sidebar frame spacing */
    [data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* Perplexity Dashboard Hero Text */
    .hero-container {
        text-align: center;
        padding-top: 50px;
        padding-bottom: 25px;
    }
    .hero-container h1 {
        font-size: 44px;
        font-weight: 700;
        letter-spacing: -1px;
        background: linear-gradient(135deg, #ffffff 40%, #ff8700 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 6px;
    }
    .hero-container p {
        color: #8a8a9e;
        font-size: 16px;
    }

    /* Translucent Translucent Content Blocks */
    .perplexity-card {
        background: rgba(18, 18, 26, 0.7);
        padding: 24px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
        margin-bottom: 20px;
    }
    
    /* Clean Minimalist styling for popover file trays */
    div[data-testid="stPopoverBody"] {
        background-color: #12121a !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# --- WORKSPACE INTERACTION HISTORY LAYER ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- CREDENTIAL SECRETS GATEWAY ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("Missing API Key! Please configure GEMINI_API_KEY inside Streamlit Secrets.")
    st.stop()

# --- AUTONOMOUS INFERENCE ROUTER SYSTEM ---
def route_and_solve_intent(prompt_text, image_b64=None, mime_type="image/jpeg"):
    # Routed to the stable production model endpoint to resolve the 404 block completely
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    system_instruction = (
        "You are an Omniscient Perplexity-style AI Assistant and Elite Code Engineer. "
        "Analyze the user's intent autonomously:\n"
        "1. For standard text interactions or greetings, provide a crisp, friendly, helpful conversational solution.\n"
        "2. For development or script creation requests, deliver production-grade code within standard markdown blocks.\n"
        "3. For visual generation requests, prepend exactly '[IMAGE_GENERATION_INTENT]' to your response followed by a highly descriptive artistic layout prompt prompt."
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
        return f"🚨 Execution Error: {str(e)}"

# --- IMAGEN 3 ERROR-FREE ART CLIENT ---
def generate_studio_canvas(prompt_text):
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
# --- PRIMARY VISUAL CONSOLE STREAM RENDER ---
# ==========================================

st.markdown("""
    <div class='hero-container'>
        <h1>Where knowledge begins.</h1>
        <p>Ask anything, compile stable scripts, generate visuals, or profile files dynamically.</p>
    </div>
""", unsafe_allow_html=True)

# Stream conversation rows natively
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "visual_art_bytes" in msg:
            st.image(msg["visual_art_bytes"], caption="Generated Studio Asset Layout", use_container_width=True)
        if "attached_dataframe" in msg:
            st.dataframe(msg["attached_dataframe"], use_container_width=True)
            st.area_chart(msg["attached_dataframe"].select_dtypes(include=['number']).head(30))

# --- FLOATING CONTROL SYSTEM (COMPACT ATTACHMENT ICON) ---
image_base64_string = None
image_mime = "image/jpeg"
uploaded_dataframe = None

# A sleek popover element acts as a premium '+' icon tray sitting cleanly right above the text row
with st.popover("➕ Add Media / Context Files"):
    st.markdown("<small style='color:#ff8700;'>Attach visual targets or metrics datasets:</small>", unsafe_allow_html=True)
    
    file_attachment = st.file_uploader("Upload contextual file target", type=["png", "jpg", "jpeg", "csv"], label_visibility="collapsed")
    if file_attachment is not None:
        filename = file_attachment.name.lower()
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            img = Image.open(file_attachment)
            st.image(img, caption="Vision Element Mapped", width=90)
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG")
            image_base64_string = base64.b64encode(buffered.getvalue()).decode("utf-8")
            st.caption("✅ Image attached")
        elif filename.endswith('.csv'):
            uploaded_dataframe = pd.read_csv(file_attachment)
            st.caption(f"✅ Data Link Active: {file_attachment.name}")

# Standard Keyboard submission bar (Sends immediately upon hitting 'Enter' and self-clears)
if user_query := st.chat_input("Ask a question, generate code blueprints, or analyze inputs..."):
    # Synthesize background indicators if file matrices exist
    final_query_payload = user_query
    if uploaded_dataframe is not None:
        final_query_payload += f"\n\n[System Context Notification: Attached file contains these columns: {uploaded_dataframe.columns.tolist()}]"
        
    with st.chat_message("user"):
        st.markdown(user_query)
        
    user_log_entry = {"role": "user", "content": user_query}
    st.session_state.chat_history.append(user_log_entry)
    
    with st.chat_message("assistant"):
        with st.spinner("Searching and processing intent..."):
            ai_reply = route_and_solve_intent(final_query_payload, image_base64_string, image_mime)
            assistant_log_entry = {"role": "assistant", "content": ai_reply}
            
            # AUTONOMOUS ROUTING TRIGGERS:
            if "[IMAGE_GENERATION_INTENT]" in ai_reply:
                clean_prompt = ai_reply.replace("[IMAGE_GENERATION_INTENT]", "").strip()
                st.markdown(f"🎨 **Auto-Routing to Image Engine:** *Generating requested art asset...*")
                art_bytes = generate_studio_canvas(clean_prompt)
                if art_bytes:
                    st.image(art_bytes, caption="Generated Studio Output Canvas", use_container_width=True)
                    assistant_log_entry["visual_art_bytes"] = art_bytes
                    assistant_log_entry["content"] = f"🎨 Generated art based on prompt blueprints:\n> {clean_prompt}"
                else:
                    st.error("Art creation pipeline was unable to compile.")
            
            elif uploaded_dataframe is not None:
                st.markdown(ai_reply)
                st.markdown("### 📈 Real-Time Automated Metric Plot")
                st.dataframe(uploaded_dataframe.head(3), use_container_width=True)
                numeric_fields = uploaded_dataframe.select_dtypes(include=['number']).columns.tolist()
                if numeric_fields:
                    st.area_chart(uploaded_dataframe[numeric_fields[0]].head(30))
                assistant_log_entry["attached_dataframe"] = uploaded_dataframe
            
            else:
                st.markdown(ai_reply)
                
            st.session_state.chat_history.append(assistant_log_entry)
            st.rerun()