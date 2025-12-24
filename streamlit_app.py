import streamlit as st
import time
import os
import vertexai
from vertexai.generative_models import GenerativeModel
from google.oauth2 import service_account

# --- 1. DYNAMIC SOP LOADER ---
def load_sop():
    try:
        # This will look for the text file you uploaded to GitHub
        with open("skyhigh_sop.txt", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "SOP file not found. Please ensure skyhigh_sop.txt is in your GitHub root."

# --- 2. INITIALIZATION (Streamlit Cloud Optimized) ---
SOP_CONTENT = load_sop()

# Load credentials from Streamlit Secrets instead of a local JSON file
# This prevents the 'DefaultCredentialsError'
try:
    creds_dict = st.secrets["gcp_service_account"]
    credentials = service_account.Credentials.from_service_account_info(creds_dict)
    
    # Initialize Vertex AI with the secure credentials object
    PROJECT_ID = "ai-training-demo-1-482218"
    vertexai.init(project=PROJECT_ID, location="europe-west2", credentials=credentials)
    
    # Load the Gemini Model
    model = GenerativeModel("gemini-2.0-flash-001")
except Exception as e:
    st.error(f"Authentication Setup Required: Please add your JSON key to Streamlit Secrets. Error: {e}")

# --- 3. STYLED HEADER ---
st.set_page_config(page_title="SkyHigh AI Learning", layout="wide")
st.title("🪂 SkyHigh: Continuous Flexible Learning")
st.markdown("---")

# --- 4. THE "FLEX" (Adaptive Entry) ---
if "user_path" not in st.session_state:
    st.session_state.user_path = None

if st.session_state.user_path is None:
    st.header("Welcome to the Hangar")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 I'm a Beginner (Full Training)"):
            st.session_state.user_path = "beginner"
            st.rerun()
            
    with col2:
        if st.button("⚖️ I'm a Pro (Jump Mentor Only)"):
            st.session_state.user_path = "pro"
            st.rerun()

# --- 5. THE "CONTINUOUS" (The Training & Mentor UI) ---
if st.session_state.user_path == "beginner":
    st.sidebar.header("Current Module: Hardware")
    st.sidebar.progress(20) 
    
    st.subheader("Visual Training: The Cut-Away")
    st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ") 
    
    st.info("💡 **Knowledge Check:** Based on SOP-CRIS-03, what is the 'Look, Grab, Pull' sequence?")
    choice = st.radio("Choose your action:", ["Pull Silver, then Red", "Pull Red, then Silver", "Pull both"])
    
    if st.button("Verify Competency"):
        if choice == "Pull Red, then Silver":
            st.success("✅ COMPETENT: You cited SOP-CRIS-03 correctly.")
            st.balloons()
            if st.button("Proceed to Jump Phase"):
                st.session_state.user_path = "pro"
                st.rerun()
        else:
            st.error("❌ INCOMPETENT: Incorrect sequence. Playing Refresher Video...")
            st.video("https://path-to-your-veo-refresher-video.mp4")

elif st.session_state.user_path == "pro":
    st.header("🛩️ Active Jump Mentor")
    st.write("The AI is now monitoring your session using the SkyHigh SOP v1.0.")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a safety question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Consulting SkyHigh SOP..."):
                # RAG Logic: Sending the user query + your specific SOP text to Gemini
                full_prompt = f"""
                You are the SkyHigh AI Mentor. 
                Answer the following question using ONLY the provided SOP text. 
                If the answer is not in the SOP, say you don't know and advise talking to an instructor.
                Always cite the specific SOP Section Code.
                
                SOP TEXT:
                {SOP_CONTENT}
                
                USER QUESTION:
                {prompt}
                """
                
                response = model.generate_content(full_prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})

# --- 6. RESET ---
if st.sidebar.button("Reset Tech Demo"):
    st.session_state.user_path = None
    st.session_state.messages = []
    st.rerun()