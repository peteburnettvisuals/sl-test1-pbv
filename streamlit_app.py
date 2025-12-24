import streamlit as st
import vertexai
from vertexai.generative_models import GenerativeModel
from google.oauth2 import service_account
if "correct_count" not in st.session_state:
    st.session_state.correct_count = 0

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
    st.video("https://www.youtube.com/watch?v=nC6D6NHjccI")
    
    # Progress Display
    st.write(f"**Mastery Level:** {st.session_state.correct_count} / 2 Correct Answers")
    st.progress(st.session_state.correct_count / 2)

    if st.button("Generate Training Scenario") or st.session_state.quiz_active:
        st.session_state.quiz_active = True
        
        # We use a JSON-like prompt to keep the answer hidden from the UI
        if "current_question_text" not in st.session_state:
            prompt = f"""
            Based on {SOP_CONTENT}, generate a tough MCQ for skydiving equipment.
            Output your response in exactly this format:
            QUESTION: [Your question and options here]
            ANSWER_KEY: [Single Letter Only]
            """
            raw_response = model.generate_content(prompt).text
            # Split the AI response to hide the key from the student
            st.session_state.current_question_text = raw_response.split("ANSWER_KEY:")[0]
            st.session_state.correct_answer = raw_response.split("ANSWER_KEY:")[1].strip()

        st.info(st.session_state.current_question_text)
        
        user_choice = st.radio("Select your answer:", ["A", "B", "C", "D"], index=None)
        
        if st.button("Submit for Instructor Review"):
            if user_choice == st.session_state.correct_answer:
                st.session_state.correct_count += 1
                st.success(f"🎯 Correct! That is {st.session_state.correct_count}/2.")
                
                # Cleanup for the next question
                del st.session_state.current_question_text
                del st.session_state.correct_answer
                
                if st.session_state.correct_count >= 2:
                    st.balloons()
                    st.session_state.training_step = 2
                    st.session_state.correct_count = 0 # Reset for the next module
                    st.session_state.quiz_active = False
                st.rerun()
            else:
                st.error("Incorrect. The instructor requires absolute precision. Refreshing for a new scenario.")
                del st.session_state.current_question_text
                st.rerun()

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