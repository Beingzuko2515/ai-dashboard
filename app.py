import streamlit as st
import pandas as pd
from google import genai
from google.genai import types
from PIL import Image
import io

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Mega AI Super-Agent Dashboard", layout="wide")
st.title("🤖 Mega AI Super-Agent Dashboard")
st.write("Welcome to your all-in-one hub for AI Chat, Live Search, Data Analytics, and Image Generation.")

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🚀 Navigation Menu")
page = st.sidebar.radio(
    "Go to Feature:", 
    ["💬 AI Agent Chat & Search", "📊 Advanced Data Analyst", "🎨 AI Image Generator", "📝 Smart Document Reader"]
)

# --- FETCH SECRET API KEY ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
    AI_MODEL = 'gemini-3.5-flash' 
except Exception:
    st.error("API Key missing! Please make sure GEMINI_API_KEY is configured in your Streamlit Secrets.")
    st.stop()

# --- FEATURE 1: AI AGENT CHAT & SEARCH ---
if page == "💬 AI Agent Chat & Search":
    st.header("💬 AI Agent Chat (With Live Search Integration)")
    st.write("Ask anything! The agent uses Google Search automatically if it needs real-time information.")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask me anything or ask me to search the web..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            
            response = client.models.generate_content(
                model=AI_MODEL,
                contents=prompt,
                config={'tools': [{'google_search': {}}]}
            )
            
            ai_response = response.text
            response_placeholder.markdown(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})

# --- FEATURE 2: ADVANCED DATA ANALYST ---
elif page == "📊 Advanced Data Analyst":
    st.header("📊 Interactive Data Analyst & Chart Generator")
    st.write("Upload any dataset (CSV) to view insights, clean tables, and plot custom charts instantly.")
    
    uploaded_file = st.file_uploader("Upload your CSV data file", type="csv")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📋 Data Preview (First 5 Rows)")
            st.dataframe(df.head())
        with col2:
            st.subheader("📈 Quick Statistics Summary")
            st.write(df.describe())
            
        st.markdown("---")
        st.subheader("🎨 Custom Chart Generator")
        numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
        
        if len(numeric_columns) >= 2:
            x_axis = st.selectbox("Select X-axis data column:", numeric_columns)
            y_axis = st.selectbox("Select Y-axis data column:", numeric_columns)
            
            chart_type = st.selectbox("Select Visual Chart Style:", ["Line Chart", "Bar Chart", "Area Chart"])
            
            chart_df = df[[x_axis, y_axis]].set_index(x_axis)
            
            if chart_type == "Line Chart":
                st.line_chart(chart_df)
            elif chart_type == "Bar Chart":
                st.bar_chart(chart_df)
            elif chart_type == "Area Chart":
                st.area_chart(chart_df)
        else:
            st.warning("Your CSV needs at least 2 numerical data columns to map visual graphs.")

# --- FEATURE 3: AI IMAGE GENERATOR ---
elif page == "🎨 AI Image Generator":
    st.header("🎨 Text-to-Image AI Canvas")
    st.write("Type a descriptive text prompt below to generate custom images using the free Gemini tier.")
    
    image_prompt = st.text_input("Enter details of the image you want to create:", placeholder="A cute futuristic robot painting on a canvas, digital art...")
    
    if st.button("Generate Image ✨"):
        if image_prompt:
            with st.spinner("Bringing your imagination to life..."):
                try:
                    # Using standard multimodal generation with an IMAGE modality request
                    response = client.models.generate_content(
                        model=AI_MODEL,
                        contents=image_prompt,
                        config=types.GenerateContentConfig(
                            response_modalities=["IMAGE"]
                        )
                    )
                    
                    image_found = False
                    for part in response.parts:
                        if part.inline_data:
                            # Convert bytes back to a displayable PIL Image format
                            image = part.as_image()
                            st.image(image, caption=f"Result for: '{image_prompt}'", use_container_width=True)
                            image_found = True
                            
                    if not image_found:
                        st.warning("The model processed your request but didn't output an image structure. Try another prompt.")
                        
                except Exception as e:
                    st.error(f"Image generation failed: {e}")
        else:
            st.warning("Please type a description prompt first!")

# --- FEATURE 4: SMART DOCUMENT READER ---
elif page == "📝 Smart Document Reader":
    st.header("📝 AI Document Summary Agent")
    st.write("Upload plain text reports or notes, and the AI will analyze them for you.")
    
    uploaded_doc = st.file_uploader("Upload a text file (.txt)", type=["txt"])
    if uploaded_doc is not None:
        stringio = io.StringIO(uploaded_doc.getvalue().decode("utf-8"))
        document_text = stringio.read()
        
        st.subheader("📑 Document Content Preview")
        st.text_area("File Context View", document_text, height=150)
        
        action = st.radio("What action should the AI perform?", ["Summarize into bullet points", "Extract action items", "Explain like I'm 5 years old"])
        
        if st.button("Analyze Document 🧠"):
            with st.spinner("Analyzing document structure..."):
                analysis_prompt = f"Please process the following text according to this directive: '{action}'. Here is the text:\n\n{document_text}"
                
                response = client.models.generate_content(
                    model=AI_MODEL,
                    contents=analysis_prompt
                )
                st.subheader("💡 AI Analysis Output")
                st.markdown(response.text)