import streamlit as st
import vertexai
from vertexai.generative_models import GenerativeModel
from google.oauth2 import service_account

# --- 1. INITIALIZATION & AUTH ---
# This part stays common to all sections
def init_vertex():
    try:
        creds_dict = st.secrets["gcp_service_account"]
        credentials = service_account.Credentials.from_service_account_info(creds_dict)
        vertexai.init(project="ai-training-demo-1-482218", location="europe-west1", credentials=credentials)
        return GenerativeModel("gemini-2.0-flash-001")
    except Exception as e:
        st.error(f"Cloud Connection Error: {e}")
        return None

model = init_vertex()

# Load SOP context once
def load_sop():
    try:
        with open("skyhigh_sop.txt", "r") as f:
            return f.read()
    except:
        return "SOP File not found."
SOP_CONTENT = load_sop()

# --- 2. SESSION STATE (The App's Memory) ---
# We use this to track training progress across pages
if "training_step" not in st.session_state:
    st.session_state.training_step = 1  # 1: Equipment, 2: Flight, 3: Crisis
if "quiz_active" not in st.session_state:
    st.session_state.quiz_active = False

# --- 3. PAGE DEFINITIONS ---

def training_module_1():
    st.title("🛠️ Phase 1: Equipment & Pre-Flight")
    st.write("Watch the video below to learn about canopy checks and weather safety.")
    st.video("https://www.youtube.com/watch?v=nC6D6NHjccI")
    
    if st.button("Start Phase 1 Quiz"):
        st.session_state.quiz_active = True
    
    if st.session_state.quiz_active:
        st.subheader("AI Verification")
        
        # 1. AI generates the question (if not already stored)
        if "current_question" not in st.session_state:
            prompt = f"Based on this SOP: {SOP_CONTENT}, generate one MCQ about pre-flight checks. End with 'Correct Answer: [Letter]'"
            st.session_state.current_question = model.generate_content(prompt).text
        
        st.info(st.session_state.current_question)
        
        # 2. THE MISSING INPUT FIELD 
        user_choice = st.radio("Select your answer:", ["A", "B", "C", "D"], index=None)
        
        # 3. VERIFICATION LOGIC
        if st.button("Submit Answer"):
            if user_choice:
                # Ask Gemini to verify the user's specific choice against the SOP
                check_prompt = f"SOP: {SOP_CONTENT}\nQuestion: {st.session_state.current_question}\nUser chose: {user_choice}. Is this correct? Answer only 'YES' or 'NO'."
                is_correct = model.generate_content(check_prompt).text
                
                if "YES" in is_correct.upper():
                    st.success(f"Correct! {user_choice} is the right procedure. Phase 2 Unlocked.")
                    st.session_state.training_step = 2
                    # Clear the quiz state for the next module
                    del st.session_state.current_question
                    st.session_state.quiz_active = False
                else:
                    st.error(f"Incorrect. Review the video and try a different question.")
                    if st.button("Generate New Question"):
                        del st.session_state.current_question
                        st.rerun()
            else:
                st.warning("Please select an option first!")

def training_module_2():
    if st.session_state.training_step < 2:
        st.warning("🔒 This module is locked. Please complete Phase 1 first.")
    else:
        st.title("🍌 Phase 2: The Jump & Maneuvers")
        st.write("Master the 'Banana' body position and your landing flare.")
        st.video("https://www.youtube.com/watch?v=ynNAC9a57ss")
        # Add similar quiz logic here to unlock Phase 3...

def active_mentor():
    st.title("🤖 Active Jump Mentor")
    st.write("Grounding Q&A enabled. Ask me anything about the SkyHigh SOP.")
    # Your existing Chatbot code (from previous version) fits here!
    user_input = st.chat_input("Ask a safety question...")
    if user_input:
        with st.chat_message("user"): st.write(user_input)
        response = model.generate_content(f"SOP Context: {SOP_CONTENT}\nUser Question: {user_input}")
        with st.chat_message("assistant"): st.write(response.text)

# --- 4. SIDEBAR NAVIGATION ---
# This generates the menu you requested
pages = {
    "Training Hangar": [
        st.Page(training_module_1, title="1. Pre-Flight", icon="🛠️"),
        st.Page(training_module_2, title="2. The Jump", icon="🍌"),
    ],
    "Operations": [
        st.Page(active_mentor, title="Live Jump Mentor", icon="🛩️"),
    ]
}

pg = st.navigation(pages)

# --- 5. SIDEBAR UTILITIES ---
with st.sidebar:
    st.write(f"**Current Progress:** Phase {st.session_state.training_step} of 3")
    if st.button("Reset Tech Demo"):
        st.session_state.training_step = 1
        st.rerun()

pg.run()