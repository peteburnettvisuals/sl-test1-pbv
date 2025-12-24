import streamlit as st
import time
import os
import vertexai
from vertexai.generative_models import GenerativeModel
SOP_CONTENT = load_sop()

# 1. Point to your downloaded key file 
# (Make sure this file is in your GitHub folder and added to .gitignore)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcp-key.json"

# 2. Initialize with your Project ID from the screenshot
PROJECT_ID = "ai-training-demo-1-482218"
vertexai.init(project=PROJECT_ID, location="us-central1")

# 3. Load the model
model = GenerativeModel("gemini-1.5-flash")

# --- 1. MOCK DATA & SOP ---
# In production, this would be a PDF/Text file loaded into Vertex AI
# --- 1. DYNAMIC SOP LOADER ---
def load_sop():
    try:
        with open("skyhigh_sop.txt", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "SOP file not found. Please upload skyhigh_sop.txt"

SOP_CONTENT = load_sop()

# --- 2. STYLED HEADER ---
st.set_page_config(page_title="SkyHigh AI Learning", layout="wide")
st.title("🪂 SkyHigh: Continuous Flexible Learning")
st.markdown("---")

# --- 3. THE "FLEX" (Adaptive Entry) ---
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

# --- 4. THE "CONTINUOUS" (The Training & Mentor UI) ---
if st.session_state.user_path == "beginner":
    st.sidebar.header("Current Module: Hardware")
    st.sidebar.progress(20) # 20% complete
    
    # VIDEO SECTION (Veo + ElevenLabs)
    st.subheader("Visual Training: The Cut-Away")
    # Replace with your local path or URL to your Veo/ElevenLabs output
    st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ") 
    
    # THE INTERACTIVE QUIZ
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
            # Here you would trigger the Module 1-B "Crisis Refresher" video
            st.video("https://path-to-your-veo-refresher-video.mp4")

elif st.session_state.user_path == "pro":
    st.header("🛩️ Active Jump Mentor")
    st.write("The AI is now monitoring your session using the SkyHigh SOP v1.0.")
    
    # CHAT INTERFACE
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
        # This is the 'Super Prompt' that gives Gemini the SOP
        full_prompt = f"""
        You are the SkyHigh AI Mentor. 
        Answer the following question using ONLY the provided SOP text. 
        If the answer is not in the SOP, say you don't know and advise talking to an instructor.
        
        SOP TEXT:
        {SOP_CONTENT}
        
        USER QUESTION:
        {prompt}
        """
        
        # Send everything to Gemini
        response = model.generate_content(full_prompt)
        
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

# --- 5. RESET (For Demo Purposes) ---
if st.sidebar.button("Reset Tech Demo"):
    st.session_state.user_path = None
    st.session_state.messages = []
    st.rerun()