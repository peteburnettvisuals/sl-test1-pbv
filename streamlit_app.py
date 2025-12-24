import streamlit as st
import time
import os
import vertexai
from vertexai.generative_models import GenerativeModel

# --- 1. DYNAMIC SOP LOADER ---
# We define this first so we can use it below
def load_sop():
    try:
        # Ensure this filename matches your uploaded .txt file exactly
        with open("skyhigh_sop.txt", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "SOP file not found. Please upload skyhigh_sop.txt"

# --- 2. INITIALIZATION ---
# Initialize SOP Content
SOP_CONTENT = load_sop()

# Point to your downloaded key file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcp-key.json"

# Initialize Vertex AI
PROJECT_ID = "ai-training-demo-1-482218"
vertexai.init(project=PROJECT_ID, location="us-central1")

# Load the Gemini Model
model = GenerativeModel("gemini-1.5-flash")

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
    # Rick Astley placeholder - replace with your Veo URL later!
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
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # CHAT LOGIC - Fixed Indentation
    if prompt := st.chat_input("Ask a safety question..."):
        # Everything from here down to st.session_state.append is now indented correctly
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Consulting SkyHigh SOP..."):
                full_prompt = f"""
                You are the SkyHigh AI Mentor. 
                Answer the following question using ONLY the provided SOP text. 
                If the answer is not in the SOP, say you don't know and advise talking to an instructor.
                
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