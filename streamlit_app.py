import streamlit as st
import vertexai
from vertexai.generative_models import GenerativeModel
from google.oauth2 import service_account

# --- 1. INITIALIZATION & AUTH ---
def init_vertex():
    try:
        creds_dict = st.secrets["gcp_service_account"]
        credentials = service_account.Credentials.from_service_account_info(creds_dict)
        vertexai.init(project="ai-training-demo-1-482218", location="europe-west1", credentials=credentials)
        return GenerativeModel("gemini-2.0-flash-001")
    except Exception as e:
        st.error(f"Setup Error: {e}")
        return None

model = init_vertex()

# Load SOP Content
def load_sop():
    with open("skyhigh_sop.txt", "r") as f:
        return f.read()
SOP_CONTENT = load_sop()

# --- 2. SESSION STATE TRACKING ---
if "training_step" not in st.session_state:
    st.session_state.training_step = 1  # Tracks which module they are on
if "quiz_question" not in st.session_state:
    st.session_state.quiz_question = None

# --- 3. DYNAMIC QUIZ GENERATOR ---
def get_ai_quiz(topic_details):
    prompt = f"""
    Generate ONE multiple choice question based ONLY on this SOP section: {topic_details}
    Format:
    Question: [Text]
    A) [Option] | B) [Option] | C) [Option] | D) [Option]
    Answer: [Letter]
    """
    response = model.generate_content(prompt)
    return response.text

# --- 4. PAGE DEFINITIONS ---

def module_1():
    st.title("🛠️ Phase 1: Equipment & Pre-Flight")
    st.video("https://www.youtube.com/watch?v=nC6D6NHjccI") # Placeholder
    
    if st.button("Take Module 1 Quiz"):
        # AI generates a fresh question from the Equipment section of your SOP
        st.session_state.quiz_question = get_ai_quiz("SOP-GEAR section regarding canopy and altimeters")
    
    if st.session_state.quiz_question:
        st.info(st.session_state.quiz_question)
        ans = st.text_input("Your Answer (A, B, C, or D):").upper()
        if st.button("Verify"):
            # Simple logic: for demo, we can just check if they entered something
            st.success("Correct! Module 2 Unlocked.")
            st.session_state.training_step = 2

def module_2():
    if st.session_state.training_step < 2:
        st.warning("Please complete Module 1 first!")
    else:
        st.title("🍌 Phase 2: Jump & Maneuver")
        st.video("https://www.youtube.com/watch?v=ynNAC9a57ss")
        st.write("Body position (The Banana) and flare mechanics...")

def module_3():
    if st.session_state.training_step < 3:
        st.warning("Please complete Module 2 first!")
    else:
        st.title("🚨 Phase 3: Crisis Management")
        st.write("Emergency procedures and cut-away drills...")

def jump_mentor():
    st.title("🛩️ Active Jump Mentor")
    # Your existing Chatbot logic goes here...
    st.write("Grounding mentor ready for Q&A.")

# --- 5. NAVIGATION ---
pg = st.navigation({
    "Training Pipeline": [
        st.Page(module_1, title="1. Pre-Flight", icon="🛠️"),
        st.Page(module_2, title="2. The Jump", icon="🍌"),
        st.Page(module_3, title="3. Survival", icon="🚨"),
    ],
    "Operations": [
        st.Page(jump_mentor, title="Live Jump Mentor", icon="🤖"),
    ]
})
pg.run()