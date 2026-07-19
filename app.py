import streamlit as st
import pandas as pd
import requests
import uuid
import base64
from PIL import Image
import io

# --- PREMIUM MIDNIGHT CONFIGURATION & HOVER GLOW LAYOUT ---
st.set_page_config(page_title="Quantum Omni Hub", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Premium Immersive Deep Dark Theme */
    .stApp {
        background-color: #0d0d14 !important;
        color: #e2e2ec !important;
    }
    
    /* Dynamic Cyber Card Panels */
    .feature-card {
        background: rgba(20, 20, 30, 0.75);
        padding: 22px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease-in-out;
        margin-bottom: 20px;
    }
    .feature-card:hover {
        border-color: rgba(255, 135, 0, 0.35);
        background: rgba(255, 135, 0, 0.01);
        box-shadow: 0 0 20px rgba(255, 135, 0, 0.06);
    }
    
    /* Inline File Drop Zone Stylings */
    div[data-testid="stFileUploader"] {
        background-color: rgba(15, 15, 25, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
        padding: 6px !important;
    }
    div[data-testid="stFileUploader"]:hover {
        border-color: #ff8700 !important;
    }
    
    /* Clean Response Chat Bubbles */
    .stChatMessage {
        border-radius: 12px;
        margin-bottom: 10px;
        border: 1px solid rgba(255, 255, 255, 0.04);
    }
    </style>
""", unsafe_allow_html=True)

# --- APPLICATION WORKSPACE STORAGE HUB ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- CORE SIDEBAR ROUTER ---
with st.sidebar:
    st.title("🔮 Core Workspace")
    st.caption("SELECT ACTIVE HUBS:")
    selected_menu = st.radio(
        "Menu Router",
        ["💬 AI Agent Chat & Code Gen", "🖼️ AI Image Studio", "📊 Interactive Data Matrix"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    if st.button("🗑️ Reset Application States", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# --- BACKEND API VAULT CONFIGURATION ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("Missing API Key! Please configure GEMINI_API_KEY inside Streamlit Secrets.")
    st.stop()

# --- RUN SECURE STABLE TEXT GATEWAY ---
def fetch_text_response(prompt_text, image_b64=None, mime_type="image/jpeg"):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    system_instruction = (
        "You are an Elite AI Assistant, Coding Sandbox, and Architecture Expert. "
        "Keep conversational greetings brief and friendly. When generating code blueprints or folder trees, "
        "always supply fully functional, clean, well-commented code scripts within standard markdown styling blocks."
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
        return f"🚨 API Connection Error ({res.status_code}): {res.text}"
    except Exception as e:
        return f"🚨 Request failed: {str(e)}"

# --- IMAGEN 3 ERROR-FREE ART STUDIO ---
def fetch_generated_art(prompt_text):
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
        return f"🚨 Studio Generation Failure: {res.json().get('error', {}).get('message', res.text)}"
    except Exception as e:
        return f"🚨 Request Error: {str(e)}"

# ==========================================
# --- WORKSPACE ROUTING MANAGEMENT VIEWS ---
# ==========================================

if selected_menu == "💬 AI Agent Chat & Code Gen":
    st.markdown("""
        <div class='feature-card'>
            <h2 style='color:#ff8700; margin-top:0;'>💬 AI Assistant & Custom Code Sandbox</h2>
            <p style='color:#9e9eaf; font-size:14px; margin-bottom:0;'>
                Execute complex prompts, generate clean scripts, or map app file directories instantly. Press <b>Enter</b> to pass commands.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Render developer tool panels
    c_lang, c_tree = st.columns(2)
    with c_lang:
        dev_lang = st.selectbox("🌐 Target Programming Language (Forces Output Tuning):", ["None / General", "Python", "JavaScript / TypeScript", "HTML & Tailwind CSS", "SQL Database Script"])
    with c_tree:
        generate_tree = st.checkbox("📂 Force AI to generate a complete visual folder structure blueprint", value=False)
        
    st.markdown("---")
    
    # Display message threads
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Minimalist inline attachment tray component
    image_base64_string = None
    uploaded_file = st.file_uploader("🖼️ Attach optional image target to conversation line context:", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        st.image(img, caption="Visual computer vision stream mapped", width=120)
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        image_base64_string = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
    st.markdown("---")
    
    # Native chat input (automatically triggers on enter and deletes old entries seamlessly)
    if user_prompt := st.chat_input("Ask a question, analyze vision data, or compile code configurations..."):
        # Synthesize custom developer instructions dynamically into the query string
        modified_prompt = user_prompt
        if dev_lang != "None / General":
            modified_prompt += f"\n\n[Developer Instruction: Explicitly format all code blocks using {dev_lang}. Ensure production stability.]"
        if generate_tree:
            modified_prompt += "\n\n[Developer Instruction: Include a clean, stylized visual ASCII folder structure diagram layout illustrating where files reside.]"
            
        with st.chat_message("user"):
            st.markdown(user_prompt)
        st.session_state.chat_history.append({"role": "user", "content": user_prompt})
        
        with st.chat_message("assistant"):
            with st.spinner("Compiling structural output vectors..."):
                reply = fetch_text_response(modified_prompt, image_base64_string)
                st.markdown(reply)
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()

elif selected_menu == "🖼️ AI Image Studio":
    st.markdown("""
        <div class='feature-card'>
            <h2 style='color:#ff8700; margin-top:0;'>🎨 Text-to-Image AI Canvas</h2>
            <p style='color:#9e9eaf; font-size:14px; margin-bottom:0;'>
                Describe ideas below to generate art elements via the error-free Imagen 3 pipeline.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    art_prompt = st.text_input("Describe visual scene ideas:", placeholder="A modern cute kitten sitting on a cyber neon desk workspace...")
    
    # Embedded dynamic toggle for prompt booster mechanics
    boost_prompt = st.checkbox("🚀 Activate Smart AI Prompt Enhancer (Injects photorealistic aesthetic framing parameters)", value=True)
    
    if st.button("Generate Asset ✨", use_container_width=True):
        if art_prompt:
            final_prompt = art_prompt
            if boost_prompt:
                with st.spinner("Text AI optimization engine running..."):
                    booster_query = f"Expand this brief sentence description into a highly vivid cinematic masterpiece generation prompt rich with lighting styles and high-detail digital rendering terms: {art_prompt}"
                    final_prompt = fetch_text_response(booster_query)
            
            with st.spinner("Generating image canvas..."):
                result = fetch_generated_art(final_prompt)
                if isinstance(result, bytes):
                    st.image(result, caption="AI Concept Masterpiece Asset", use_container_width=True)
                else:
                    st.error(result)
        else:
            st.warning("Please type a scene description layout details first!")

elif selected_menu == "📊 Interactive Data Matrix":
    st.markdown("""
        <div class='feature-card'>
            <h2 style='color:#ff8700; margin-top:0;'>📊 Interactive Analytics Grid</h2>
            <p style='color:#9e9eaf; font-size:14px; margin-bottom:0;'>
                Upload a structured file table (.csv) below to parse indicators and render multi-style graphs.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    csv_file = st.file_uploader("Upload dataset target table:", type=["csv"])
    if csv_file is not None:
        df = pd.read_csv(csv_file)
        st.success("Matrix successfully parsed into active dataframe!")
        st.dataframe(df.head(5), use_container_width=True)
        
        st.markdown("---")
        st.subheader("📈 Dynamic Multi-Variable Plotting Station")
        numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
        
        if numeric_columns:
            c_target, c_style = st.columns(2)
            with c_target:
                target_col = st.selectbox("Choose data parameter row to inspect visually:", numeric_columns)
            with c_style:
                chart_style = st.selectbox("Select Visual Chart Engine Mode:", ["Line Chart", "Area Chart", "Bar Chart"])
            
            # Draw real-time graphics frames
            if chart_style == "Line Chart":
                st.line_chart(df[target_col].head(40))
            elif chart_style == "Area Chart":
                st.area_chart(df[target_col].head(40))
            elif chart_style == "Bar Chart":
                st.bar_chart(df[target_col].head(40))
                
            st.markdown("---")
            if st.button("Extract Deep Context Data Summaries 📝", use_container_width=True):
                with st.spinner("Calculating mathematical matrix summaries..."):
                    analytics_query = f"Provide a clean, bulleted data metrics analysis profiling columns: {df.columns.tolist()}. Identify insights based on these row headers."
                    ans = fetch_text_response(analytics_query)
                    st.info(ans)
        else:
            st.warning("No functional numeric variables detected inside the selected sheet format to plot graphic charts.")