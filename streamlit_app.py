import streamlit as st
import time

# --- 1. MOCK DATA & SOP ---
# In production, this would be a PDF/Text file loaded into Vertex AI
SOP_CONTENT = {
    "SOP-GEAR-01": "The Red Handle (Chest) releases the main chute. The Silver Handle (Hip) deploys the reserve.",
    "SOP-CRIS-03": "In a malfunction, 'Look, Grab, Pull' the Red handle first, then the Silver.",
    "SOP-NAV-01": "To Flare: Pull both toggles to waist height at 10ft altitude."
}

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

        # SIMULATED VERTEX AI RESPONSE
        with st.chat_message("assistant"):
            if "water" in prompt.lower():
                response = f"**EMERGENCY:** {SOP_CONTENT['SOP-NAV-01']} is not for water. Refer to **SOP-CRIS-02**: Unclip chest strap, but keep leg straps until impact."
            elif "spin" in prompt.lower() or "twist" in prompt.lower():
                response = "According to **SOP-CRIS-01**, grab risers and bicycle kick. You have until 2,500ft to clear."
            else:
                response = "I am monitoring. Please focus on your altimeter. Refer to SOP-GEAR-02 for deployment heights."
            
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

# --- 5. RESET (For Demo Purposes) ---
if st.sidebar.button("Reset Tech Demo"):
    st.session_state.user_path = None
    st.session_state.messages = []
    st.rerun()