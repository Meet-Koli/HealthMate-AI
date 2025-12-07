import streamlit as st
import google.generativeai as genai
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# SECURE: Get key from Streamlit Secrets (for Cloud) or Environment Variables
try:
    if "GOOGLE_API_KEY" in st.secrets:
        GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    else:
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
except FileNotFoundError:
    st.error("API Key not found. Please set it in secrets.toml or environment variables.")
    st.stop()

# Configure the Gemini API
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash') 
except Exception as e:
    st.error(f"Error configuring API: {e}. Please check your API Key.")

# Page Setup
st.set_page_config(
    page_title="HealthMate AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. CUSTOM CSS (Fixed Dropdown Colors)
# ==========================================
st.markdown("""
    <style>
    /* 1. Main Background */
    .stApp {
        background: linear-gradient(135deg, #ffffff 0%, #e8f5e9 100%);
    }
    
    /* 2. Normal Text */
    .stMarkdown, p, li, .stText, .stChatInput {
        color: #111111 !important;
        font-size: 19px !important;
        font-weight: 500 !important;
        line-height: 1.6 !important;
    }

    /* 3. Headers */
    h1, h2, h3, .main-header {
        color: #1b5e20 !important;
        font-weight: 800 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }

    /* 4. Buttons */
    div.stButton > button {
        background: linear-gradient(135deg, #2e7d32 0%, #43a047 100%);
        color: white !important;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        padding: 12px 28px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%);
        transform: scale(1.02);
    }

    /* 5. WIDGET LABELS (Questions) */
    label, .stSelectbox label, .stSlider label, .stRadio label {
        color: #1b5e20 !important; /* Dark Green */
        font-size: 20px !important;
        font-weight: 700 !important;
    }

    /* 6. FIX: DROPDOWN MENU COLORS */
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul {
        background-color: #ffffff !important;
    }
    li[data-baseweb="option"] {
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
        border-color: #2e7d32 !important;
    }
            
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #f1f8e9;
        border-right: 2px solid #c8e6c9;
    } 
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================
def get_ai_response(user_prompt, system_role):
    """Sends a prompt to Gemini with a specific persona/system role."""
    try:
        full_prompt = f"{system_role}\n\nUser Query: {user_prompt}"
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# ==========================================
# 4. SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.title("🏥 HealthMate")
    st.write("AI Health Assistant")
    
    menu = st.radio(
        "Navigate", 
        ["Symptom Checker", "Mental Health", "Health Tips", "Health Assessment"]
    )
    
    st.markdown("---")
    st.info("⚠️ **Note:** This is an AI assistant. Always consult a doctor for medical emergencies.")

# ==========================================
# 5. MAIN APPLICATION LOGIC
# ==========================================

# --- SYMPTOM CHECKER ---
if menu == "Symptom Checker":
    st.markdown("<h1 class='main-header'>🔍 AI Symptom Checker</h1>", unsafe_allow_html=True)
    st.write("Describe your symptoms, and I will provide basic guidance and recommendations.")

    if "symptom_messages" not in st.session_state:
        st.session_state.symptom_messages = []

    for message in st.session_state.symptom_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ex: I have a headache and mild fever..."):
        st.session_state.symptom_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing symptoms..."):
                system_prompt = "You are a helpful AI health assistant. Analyze symptoms and provide BRIEF guidance. Use bullet points. Always remind users to consult healthcare professionals for serious concerns."
                response = get_ai_response(prompt, system_prompt)
                st.markdown(response)
        
        st.session_state.symptom_messages.append({"role": "assistant", "content": response})

# --- MENTAL HEALTH ---
elif menu == "Mental Health":
    st.markdown("<h1 class='main-header'>💙 Mental Health Companion</h1>", unsafe_allow_html=True)
    
    st.subheader("How are you feeling today?")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    mood = None
    if col1.button("😊 Great"): mood = "Great"
    if col2.button("🙂 Good"): mood = "Good"
    if col3.button("😐 Okay"): mood = "Okay"
    if col4.button("😔 Sad"): mood = "Sad"
    if col5.button("😰 Anxious"): mood = "Anxious"

    if "mental_messages" not in st.session_state:
        st.session_state.mental_messages = []

    if mood:
        mood_responses = {
            "Great": "That's wonderful! 😊 What's making you feel great today?",
            "Good": "Happy to hear that! 🙂 Keep nurturing those positive feelings.",
            "Sad": "I'm sorry you're feeling sad. 😔 It's okay to feel this way. Want to talk about it?",
            "Anxious": "Anxiety can be tough. 😰 Try breathing: In for 4, Hold for 4, Out for 4.",
            "Okay": "It's okay to just be okay. 😐 Anything on your mind?"
        }
        response = mood_responses.get(mood, "Tell me more.")
        st.session_state.mental_messages.append({"role": "assistant", "content": response})

    for message in st.session_state.mental_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Share your thoughts..."):
        st.session_state.mental_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Listening..."):
                system_prompt = "You are a compassionate mental health companion. Provide brief emotional support. If someone mentions self-harm, encourage professional help immediately."
                response = get_ai_response(prompt, system_prompt)
                st.markdown(response)
        
        st.session_state.mental_messages.append({"role": "assistant", "content": response})

# --- HEALTH TIPS ---
elif menu == "Health Tips":
    st.markdown("<h1 class='main-header'>📚 Health Education</h1>", unsafe_allow_html=True)
    
    tips = [
        "💧 Drink at least 8 glasses of water daily.",
        "🏃 Aim for 30 minutes of moderate exercise daily.",
        "😴 Get 7-9 hours of quality sleep each night.",
        "🥗 Include colorful fruits and vegetables in your diet.",
        "🧘 Practice deep breathing for 5 minutes daily."
    ]
    
    if st.button("💡 Get a Random Health Tip"):
        st.success(f"**Tip of the moment:** {random.choice(tips)}")

    st.markdown("### Ask the Health Educator")
    if "edu_messages" not in st.session_state:
        st.session_state.edu_messages = []

    for message in st.session_state.edu_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask about nutrition, exercise, etc..."):
        st.session_state.edu_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Researching..."):
                system_prompt = "You are a knowledgeable health educator. Provide brief, evidence-based health information. Use bullet points."
                response = get_ai_response(prompt, system_prompt)
                st.markdown(response)
        
        st.session_state.edu_messages.append({"role": "assistant", "content": response})

# --- HEALTH ASSESSMENT ---
elif menu == "Health Assessment":
    st.markdown("<h1 class='main-header'>📋 Health Assessment</h1>", unsafe_allow_html=True)
    st.write("Answer these **10 lifestyle questions** to get a personalized health summary.")
    
    with st.form("health_assessment_form"):
        # Group 1: Daily Routine
        st.subheader("1️⃣ Daily Routine & Energy")
        col1, col2 = st.columns(2)
        with col1:
            q1 = st.selectbox("1. Daily Energy Levels", ["High/Energetic", "Moderate/Consistent", "Low/Fatigued", "Ups and Downs"])
            q2 = st.selectbox("2. Screen Time (Daily)", ["Less than 2 hours", "2-4 hours", "4-8 hours", "8+ hours"])
        with col2:
            q3 = st.selectbox("3. Time spent outdoors/nature", ["Daily", "Few times a week", "Rarely", "Never"])
            q4 = st.selectbox("4. Social Connection Frequency", ["Daily", "Weekly", "Monthly", "Rarely"])
        
        # Group 2: Habits & Diet
        st.subheader("2️⃣ Habits & Diet")
        col3, col4 = st.columns(2)
        with col3:
            q5 = st.select_slider("5. Physical Activity", options=["Sedentary", "Light", "Moderate", "Active", "Athlete"])
            q6 = st.selectbox("6. Daily Water Intake", ["Less than 1L", "1-2 Liters", "2-3 Liters", "More than 3L"])
        with col4:
            q7 = st.selectbox("7. Sleep Quality", ["Restful", "Okay", "Disturbed", "Insomnia"])
            q8 = st.selectbox("8. Diet Quality", ["Mostly Home Cooked", "Balanced", "Often Processed/Fast Food", "Unhealthy"])

        # Group 3: Wellness
        st.subheader("3️⃣ Mental Wellness")
        col5, col6 = st.columns(2)
        with col5:
            q9 = st.slider("9. Current Stress Level (1=Low, 10=High)", 1, 10, 5)
        with col6:
            q10 = st.selectbox("10. General Mood Lately", ["Happy/Content", "Neutral/Okay", "Stressed/Anxious", "Low/Sad"])

        st.markdown("---")
        submitted = st.form_submit_button("✅ Generate Health Report")
        
        if submitted:
            user_data = f"""
            Energy: {q1}. Screen Time: {q2}. Outdoor Time: {q3}. Social: {q4}.
            Activity: {q5}. Water: {q6}. Sleep: {q7}. Diet: {q8}.
            Stress: {q9}/10. Mood: {q10}.
            """
            
            with st.spinner("🤖 AI is analyzing your health habits..."):
                prompt = f"""
                Act as a professional health consultant. Analyze this user profile based on 10 lifestyle markers:
                {user_data}
                Please provide a friendly health report including Routine Analysis, Lifestyle Score, and 3 Actionable Tips.
                """
                response = get_ai_response(prompt, "You are an expert health analyst.")
                
            st.success("Assessment Complete!")
            st.markdown("### 🩺 Your Personalized Health Report")

            st.markdown(response)

