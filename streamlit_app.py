import streamlit as st

# --- BRANDING & STYLING ---
st.set_page_config(page_title="SkyHigh AI Training", page_icon="🪂")

st.markdown("""
    <style>
        /* 1. Page Background Gradient */
        .stApp {
            background: linear-gradient(180deg, #ffffff 0%, #e8f1f8 100%);
        }

        /* 2. Sidebar Logo Placement & Sidebar Font Size */
        [data-testid="stSidebarNav"] span {
            font-size: 1.1rem !important;
            font-weight: 500 !important;
        }
        
        /* Sidebar Group Headers (e.g., 'Training Hangar') */
        [data-testid="sidebar-nav-item-group"] {
            font-size: 1.2rem !important;
            color: #d32f2f !important; /* SkyHigh Red */
            font-weight: bold !important;
        }

        /* 3. Custom Radio Button Text Size */
        .stRadio label {
            font-size: 1.1rem !important;
        }
    </style>
""", unsafe_allow_html=True)

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


# --- Home Screen

def welcome_home():
    st.title("Welcome to SkyHigh AI Training")

    st.video("https://youtu.be/oX3PB6_zrCU")

    st.markdown("""
    ### Purpose of this Demo
    This tech demo from Pete Burnett Visuals uses **Gemini 2.0 Flash** to ensure every jumper is 100% prepared for the skies. 
    Unlike static tests, our AI instructor generates dynamic scenarios, with all questions and responses based solely on real SOPs.
    
    ### How it Works
    1. **Mastery Modules**: You must pass 3 phases (PreFlight, Jump, and Crisis).
    2. **The 2/2 Rule**: You must answer two consecutive questions correctly to progress.
    3. **Live Mentor**: Once graduated, you unlock a real-time safety assistant.
                
    ### Using a mobile?
    There is a sidebar that you can open and close by clicking on the double arrows at the top left of the screen.            
    """)
    if st.button("Begin Training"):
        st.switch_page(st.Page(training_module_1))

# --- PHASE 1: EQUIPMENT ---
def training_module_1():
    st.title("Phase 1: Equipment & Pre-Flight")
    st.video("https://www.youtube.com/watch?v=74DSBbwm_UY")

    st.markdown("""
    ### First, watch the training video above. 
    There is a small amount of information to take in, so we have highlighted the important bits with friendly arrows!
    
    ### Then, try the assessment below.
    You'll need to get 2 right answers in a row to pass this section. All of the questions are generated uniquely for each user, to make sure that the assessment is accurate!  
    """)
    
    st.write(f"**Mastery Level:** {st.session_state.count_m1} / 2 Correct")
    st.progress(st.session_state.count_m1 / 2)

    if st.session_state.count_m1 == 0:
        focus1 = "Focus strictly on the cumulo-nimbus WEATHER condition mentioned in SOP-ENV-01."
    else:
        focus1 = "Focus strictly on HARNESS and ALTIMETER checks found in SOP-GEAR-02."

    if st.button("Generate Gear Scenario") or st.session_state.quiz_active:
        st.session_state.quiz_active = True
        
        if "current_question_text" not in st.session_state:
            # Focus prompt on SOP-GEAR
            prompt = f"""
Based ONLY on SECTION 1 of this SOP: {SOP_CONTENT}, {focus1},
STRICT RULE: Only ONE of the four lettered options (A, B, C, or D) can be factually correct according to the SOP.
            The other three options must be definitively WRONG based on the text, as the user will be answering with radio buttons and cannot mutiple select. 
            Avoid "All of the above", "some of the above" or "None of the above" scenarios.
            You MUST include the lettered answer options in the question.
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
                    # 2. Add a pause so they see the balloons and success message
                    time.sleep(3) 
                    # 3. Jump to next module
                    st.switch_page(st.Page(training_module_2))
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
        st.title("Phase 2: The Jump & Maneuvers")
        st.video("https://www.youtube.com/watch?v=iQcRGqhIbLo")

        st.markdown("""
        ### Like before, watch the training video above. 
        Shorter and easier one this time!
    
        ### Then, try the assessment below.
        You'll need to get 2 right answers in a row to pass this section. Can you do it first go?  
        """)
        
        st.write(f"**Mastery Level:** {st.session_state.count_m2} / 2 Correct")
        st.progress(st.session_state.count_m2 / 2)

        if st.session_state.count_m2 == 0:
        # Hard isolation: The AI is forbidden from mentioning navigation
            focus2 = """
            Focus EXCLUSIVELY on the 'Stable Arch' (The Banana) body position and aircraft exit. 
            STRICT PROHIBITION: Do NOT mention toggles, steering, turns, or flares. 
            If the question mentions a parachute handle or steering, it is a failure of this instruction.
            """
        else:
        # Shift focus to landing patterns specifically to avoid basic steering loops
            focus2 = """
            Focus EXCLUSIVELY on the falre technique (SOP-NAV-01). 
            STRICT PROHIBITION: Do NOT ask about basic left/right turns or 'how to steer'. 
            Focus on altitudes for the downwind or base leg.
            """

        if st.button("Generate Jump Scenario") or st.session_state.quiz_active:
            st.session_state.quiz_active = True
            if "current_question_text" not in st.session_state:
                # Focus prompt on Body Position and Flare
                prompt = f"""
Based ONLY on SECTION 2 of this SOP: {SOP_CONTENT}, {focus2},
STRICT RULE: Only ONE of the four lettered options (A, B, C, or D) can be factually correct according to the SOP.
            The other three options must be definitively WRONG based on the text, as the user will be answering with radio buttons and cannot mutiple select. 
            Avoid "All of the above" or "None of the above" scenarios.
            You MUST include the lettered answer options in the question.
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
                        st.success("🎯 Mastery achieved! Phase 3: Crisis Mgmt is now unlocked.")
                        st.session_state.training_step = 3
                        st.session_state.quiz_active = False
                        del st.session_state.current_question_text
                        # 2. Add a pause so they see the balloons and success message
                        time.sleep(3) 
                        # 3. Jump to next module
                        st.switch_page(st.Page(training_module_3)) 
                    else:
                        st.toast("Solid form! One more.", icon="✅")
                        del st.session_state.current_question_text
                        st.rerun()
                else:
                    st.error("❌ Incorrect. Precision in the air is vital. Progress reset.")
                    time.sleep(2)
                    st.session_state.count_m2 = 0
                    del st.session_state.current_question_text
                    st.rerun()

# --- PHASE 3: SURVIVAL ---
def training_module_3():
    if st.session_state.training_step < 3:
        st.warning("🔒 Complete Phase 2 to unlock this module.")
    else:
        st.title("Phase 3: Crisis Management")
        st.video("https://www.youtube.com/watch?v=3qDBFceGupU")

        st.markdown("""
        ### Last video on this course! 
        Almost there!
    
        ### And then, your final assessment below.
        You are just 2 correct answers away from one of the most pointless certifications you will ever get. But you do get balloons with it.
        """)
        
        st.write(f"**Mastery Level:** {st.session_state.count_m3} / 2 Correct")
        st.progress(st.session_state.count_m3 / 2)

        if st.session_state.count_m3 == 0:
            focus3 = "Focus strictly on water landings covered in SOP-CRIS-02."
        else:
            focus3 = "Focus strictly on cut away procedure covered in SOP-CRIS-03."

        if st.button("Generate Crisis Scenario") or st.session_state.quiz_active:
            st.session_state.quiz_active = True
            if "current_question_text" not in st.session_state:
                # Focus prompt on SOP-CRIS (Emergency procedures)
                prompt = f"""
Based ONLY on SECTION 3 of this SOP: {SOP_CONTENT}, {focus3}
STRICT RULE: Only ONE of the four lettered options (A, B, C, or D) can be factually correct according to the SOP.
            The other three options must be definitively WRONG based on the text, as the user will be answering with radio buttons and cannot mutiple select. 
            Avoid "All of the above" or "None of the above" scenarios.
            You MUST include the lettered answer options in the question.
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
                    st.rerun()

def active_mentor():
    st.title("🤖 Active Jump Mentor")
    st.write("This is a live Q&A assistant for qualified SkyHigh graduates. All questions will be answered based exclusively on the SkyHigh SOP. This demo uses a system called RAG to ensure that all answers are correct and no AI hallucinations will be returned. Give it a go!")
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
    st.write("You are now officially cleared to use the **Active Jump Mentor** for real-time mission support. You can find it in the sidebar menu, under Operations.")
    
    # Show a mock certificate
    st.info("CERTIFICATE ID: SH-2025-" + str(st.session_state.count_m1 + 99))



# --- 4. SIDEBAR NAVIGATION ---

st.sidebar.image("TECHDEMO.png", use_container_width=True)
# 1. Start with the pages everyone can see
pages = {
    "Start Here": [st.Page(welcome_home, title="Welcome", icon="🏠")],
    "Training Hangar": [
        st.Page(training_module_1, title="1. Pre-Flight", icon="🛠️"),
        st.Page(training_module_2, title="2. The Jump", icon="🍌"),
        st.Page(training_module_3, title="3. Crisis Mgmt", icon="🚨"),
    ]
}

# 2. Add Graduation AND Operations only if they passed Phase 3
if st.session_state.training_step > 3:
    # Add Graduation to the Training Hangar list
    pages["Training Hangar"].append(st.Page(graduation_screen, title="Graduation", icon="🎓"))
    
    # Create the Operations section from scratch
    pages["Operations"] = [st.Page(active_mentor, title="Live Jump Mentor", icon="🛩️")]

# 3. Finalize Navigation
pg = st.navigation(pages)

# --- 5. SIDEBAR UTILITIES ---
with st.sidebar:
    st.write(f"**Current Progress:** You are at stage {st.session_state.training_step} of 4")
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