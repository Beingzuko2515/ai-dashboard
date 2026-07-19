import streamlit as st
import pandas as pd
import google.generativeai as genai
import io

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Mega AI Super-Agent Dashboard", layout="wide")
st.title("🤖 Mega AI Super-Agent Dashboard")
st.write("Welcome to your all-in-one hub for AI Chat, Data Analytics, and Document Insights.")

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🚀 Navigation Menu")
page = st.sidebar.radio(
    "Go to Feature:", 
    ["💬 AI Agent Chat", "📊 Advanced Data Analyst", "🎨 AI Art Concept Generator", "📝 Smart Document Reader"]
)

# --- FETCH SECRET API KEY ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    # Using the most globally compatible free text model
    model = genai.GenerativeModel('gemini-pro') 
except Exception:
    st.error("API Key missing! Please make sure GEMINI_API_KEY is configured in your Streamlit Secrets.")
    st.stop()

# --- FEATURE 1: AI AGENT CHAT ---
if page == "💬 AI Agent Chat":
    st.header("💬 AI Agent Chat")
    st.write("Ask anything! The agent will use its knowledge base to solve problems.")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask me anything..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            try:
                response = model.generate_content(prompt)
                ai_response = response.text
                response_placeholder.markdown(ai_response)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
            except Exception as e:
                st.error(f"Chat failed to load: {e}")

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

# --- FEATURE 3: AI ART CONCEPT GENERATOR ---
elif page == "🎨 AI Art Concept Generator":
    st.header("🎨 AI Art Concept Engine")
    st.write("This feature uses AI to expand your idea into beautiful, highly detailed artwork prompt descriptions and structure layouts.")
    
    image_prompt = st.text_input("Enter a basic art idea:", placeholder="A cute robot painting on a canvas...")
    
    if st.button("Generate Concept Design ✨"):
        if image_prompt:
            with st.spinner("Expanding your design concepts..."):
                try:
                    art_prompt = f"Act as an expert digital artist. Create a highly descriptive layout blueprint, color palette, lighting details, and Midjourney style prompts based on this idea: '{image_prompt}'"
                    response = model.generate_content(art_prompt)
                    st.subheader("💡 Digital Art Blueprint")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Failed to generate layout: {e}")
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
                try:
                    analysis_prompt = f"Please process the following text according to this directive: '{action}'. Here is the text:\n\n{document_text}"
                    response = model.generate_content(analysis_prompt)
                    st.subheader("💡 AI Analysis Output")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Analysis failed: {e}")