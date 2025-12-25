import streamlit as st
import vertexai
import time
from vertexai.generative_models import GenerativeModel
from google.oauth2 import service_account
if "count_m1" not in st.session_state:
    st.session_state.count_m1 = 0
if "count_m2" not in st.session_state:
    st.session_state.count_m2 = 0
if "count_m3" not in st.session_state:
    st.session_state.count_m3 = 0

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

# --- PHASE 1: EQUIPMENT ---
def training_module_1():
    st.title("🛠️ Phase 1: Equipment & Pre-Flight")
    st.video("https://www.youtube.com/watch?v=nC6D6NHjccI")
    
    st.write(f"**Mastery Level:** {st.session_state.count_m1} / 2 Correct")
    st.progress(st.session_state.count_m1 / 2)

    if st.button("Generate Gear Scenario") or st.session_state.quiz_active:
        st.session_state.quiz_active = True
        
        if "current_question_text" not in st.session_state:
            # Focus prompt on SOP-GEAR
            prompt = f"""
Based ONLY on the SECTION 1: PRE-FLIGHT & EQUIPMENT section of this SOP: {SOP_CONTENT}
Generate one MCQ. 
STRICT RULE: Do NOT ask about line twists, cut-aways, or malfunctions.
Focus ONLY on gear checks, weather minimums, or altimeters.  You MUST include the lettered answer options in the question.
Output: QUESTION: [text] ANSWER_KEY: [Letter]  
"""
            raw_response = model.generate_content(prompt).text
            st.session_state.current_question_text = raw_response.split("ANSWER_KEY:")[0]
            st.session_state.correct_answer = raw_response.split("ANSWER_KEY:")[1].strip()

        st.info(st.session_state.current_question_text)
        user_choice = st.radio("Select answer:", ["A", "B", "C", "D"], index=None, key=f"m1_radio_{st.session_state.count_m1}")
        
        if st.button("Submit Phase 1 Answer"):
            if user_choice == st.session_state.correct_answer:
                st.session_state.count_m1 += 1
                if st.session_state.count_m1 >= 2:
                    st.balloons()
                    st.success("🎯 Mastery achieved! Phase 2: The Jump is now unlocked.")
                    st.session_state.training_step = 2
                    st.session_state.quiz_active = False
                    del st.session_state.current_question_text 
                else:
                    st.toast("Great job! One more.", icon="✅")
                    del st.session_state.current_question_text
                    st.rerun()
            else:
                st.error("❌ Incorrect. Gear safety is binary. Progress reset.")
                time.sleep(2)
                st.session_state.count_m1 = 0
                del st.session_state.current_question_text
                st.rerun()

# --- PHASE 2: MANEUVER ---
def training_module_2():
    if st.session_state.training_step < 2:
        st.warning("🔒 Complete Phase 1 to unlock this module.")
    else:
        st.title("🍌 Phase 2: The Jump & Maneuvers")
        st.video("https://www.youtube.com/watch?v=ynNAC9a57ss")
        
        st.write(f"**Mastery Level:** {st.session_state.count_m2} / 2 Correct")
        st.progress(st.session_state.count_m2 / 2)

        if st.button("Generate Flight Scenario") or st.session_state.quiz_active:
            st.session_state.quiz_active = True
            if "current_question_text" not in st.session_state:
                # Focus prompt on Body Position and Flare
                prompt = f"""
Based ONLY on the SECTION 2: THE JUMP & MANEUVERS (SKILLS PHASE) section of this SOP: {SOP_CONTENT}
Generate one MCQ. 
STRICT RULE: Focus ONLY on body position (banana), or steering, or landing flares.
Do NOT ask about emergency procedures or malfunction heights. You MUST include the lettered answer options in the question.
Output: QUESTION: [text] ANSWER_KEY: [Letter]
"""
                raw_response = model.generate_content(prompt).text
                st.session_state.current_question_text = raw_response.split("ANSWER_KEY:")[0]
                st.session_state.correct_answer = raw_response.split("ANSWER_KEY:")[1].strip()

            st.info(st.session_state.current_question_text)
            user_choice = st.radio("Select answer:", ["A", "B", "C", "D"], index=None, key=f"m2_radio_{st.session_state.count_m2}")
            
            if st.button("Submit Phase 2 Answer"):
                if user_choice == st.session_state.correct_answer:
                    st.session_state.count_m2 += 1
                    if st.session_state.count_m2 >= 2:
                        st.balloons()
                        st.success("🎯 Mastery achieved! Phase 3: Survival is now unlocked.")
                        st.session_state.training_step = 3
                        st.session_state.quiz_active = False
                        del st.session_state.current_question_text 
                    else:
                        st.toast("Solid form! One more.", icon="✅")
                        del st.session_state.current_question_text
                        st.rerun()
                else:
                    st.error("❌ Incorrect. Precision in the air is vital. Progress reset.")
                    time.sleep(2)
                    st.session_state.count_m2 = 0
                    del st.session_state.current_question_text
                    key=f"m2_radio_{st.session_state.count_m2}"
                    st.rerun()

# --- PHASE 3: SURVIVAL ---
def training_module_3():
    if st.session_state.training_step < 3:
        st.warning("🔒 Complete Phase 2 to unlock this module.")
    else:
        st.title("🚨 Phase 3: Crisis Management")
        st.video("https://www.youtube.com/watch?v=nC6D6NHjccI")
        
        st.write(f"**Mastery Level:** {st.session_state.count_m3} / 2 Correct")
        st.progress(st.session_state.count_m3 / 2)

        if st.button("Generate Crisis Scenario") or st.session_state.quiz_active:
            st.session_state.quiz_active = True
            if "current_question_text" not in st.session_state:
                # Focus prompt on SOP-CRIS (Emergency procedures)
                prompt = f"""
Based ONLY on the SECTION 3: CRISIS MANAGEMENT section of this SOP: {SOP_CONTENT}
Generate one MCQ. 
STRICT RULE: Focus ONLY on emergency procedures, malfunction identification, and cut-away protocols. 
            Do NOT ask about body position, landing flares, or normal steering.  You MUST include the lettered answer options in the question.
Output: QUESTION: [text] ANSWER_KEY: [Letter]
"""
                raw_response = model.generate_content(prompt).text
                st.session_state.current_question_text = raw_response.split("ANSWER_KEY:")[0]
                st.session_state.correct_answer = raw_response.split("ANSWER_KEY:")[1].strip()

            st.info(st.session_state.current_question_text)
            user_choice = st.radio("Select answer:", ["A", "B", "C", "D"], index=None, key=f"m3_radio_{st.session_state.count_m3}")
            
            if st.button("Submit Phase 3 Answer"):
                if user_choice == st.session_state.correct_answer:
                    st.session_state.count_m3 += 1
                    if st.session_state.count_m3 >= 2:
                        st.balloons()
                        st.success("🎯 Course Complete! You are now cleared for the Active Jump Mentor.")
                        st.session_state.training_step = 4
                        st.session_state.quiz_active = False
                        del st.session_state.current_question_text 
                        # 2. Add a pause so they see the balloons and success message
                        time.sleep(3) 
                        # 3. Jump to grad page
                        st.switch_page(st.Page(graduation_screen))
                    else:
                        st.toast("Cool under pressure! One more.", icon="✅")
                        del st.session_state.current_question_text
                        st.rerun()
                else:
                    st.error("❌ Incorrect. In a crisis, there is no room for error. Progress reset.")
                    time.sleep(2)
                    st.session_state.count_m3 = 0
                    del st.session_state.current_question_text
                    key=f"m3_radio_{st.session_state.count_m2}"
                    st.rerun()

def active_mentor():
    st.title("🤖 Active Jump Mentor")
    st.write("Grounding Q&A enabled. Ask me anything about the SkyHigh SOP.")
    # Your existing Chatbot code (from previous version) fits here!
    user_input = st.chat_input("Ask a safety question...")
    if user_input:
        with st.chat_message("user"): st.write(user_input)
        response = model.generate_content(f"SOP Context: {SOP_CONTENT}\nUser Question: {user_input}")
        with st.chat_message("assistant"): st.write(response.text)

def graduation_screen():
    st.balloons()
    st.title("🎓 Certified SkyHigh Jumper")
    st.success("Congratulations! You have mastered all three phases of the SkyHigh SOP.")
    st.write("You are now officially cleared to use the **Active Jump Mentor** for real-time mission support.")
    
    # Show a mock certificate
    st.info("CERTIFICATE ID: SH-2025-" + str(st.session_state.count_m1 + 99))



# --- 4. SIDEBAR NAVIGATION ---
# This generates the menu you requested
pages = {
    "Training Hangar": [
        st.Page(training_module_1, title="1. Pre-Flight", icon="🛠️"),
        st.Page(training_module_2, title="2. The Jump", icon="🍌"),
        st.Page(training_module_3, title="3. Crisis Mgmt", icon="🚨"),
    ],
        # Update your navigation logic to include the graduation if training is complete
        "Operations": [
        st.Page(active_mentor, title="Live Jump Mentor", icon="🛩️"),
    ]
}

if st.session_state.training_step > 3:
    pages["Training Hangar"].append(st.Page(graduation_screen, title="Graduation", icon="🎓"))
    

pg = st.navigation(pages)

# --- 5. SIDEBAR UTILITIES ---
with st.sidebar:
    st.write(f"**Current Progress:** Passed {st.session_state.training_step} of 3 Modules")
    if st.button("Reset Tech Demo"):
        st.session_state.training_step = 1
        st.session_state.count_m1 = 0
        st.session_state.count_m2 = 0
        st.session_state.count_m3 = 0

        # CLEAR THE AI CACHE
        # This removes the "Current Question" so the next one is truly fresh
        if "current_question_text" in st.session_state:
            del st.session_state.current_question_text
        if "correct_answer" in st.session_state:
            del st.session_state.correct_answer
        st.rerun()

pg.run()