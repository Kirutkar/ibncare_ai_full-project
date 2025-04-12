# --- 📦 Imports ---
import streamlit as st
import requests
import speech_recognition as sr
import random
from PIL import Image
import random
import string
import os


# --- 🌐 Backend URL ---
BACKEND_URL = "https://ibncareai-backend.onrender.com"


# --- 🧠 Initialize Session State ---
defaults = {
    "user_input": "",
    "chat_response": "",
    "user_name_chat": "",
    "gender_chat": "Select",
    "age_chat": 0,
    "user_name_symptom": "",
    "gender_symptom": "Select",
    "age_symptom": 0,
    "symptom_input": "",
    "medical_user_name": "",
    "gender_medical": "Select",
    "age_medical": 0,
    "condition_type": "",
    "condition_description": "",
    "medical_history_data": [],
    "chat_history": [],
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

if "symptom_input_key" not in st.session_state:
    st.session_state["symptom_input_key"] = "symptom_input_box"
if "age_symptom_key" not in st.session_state:
    st.session_state["age_symptom_key"] = "age_symptom_box"
if "pdf_ready" not in st.session_state:
    st.session_state["pdf_ready"] = False
if "show_scan_uploader" not in st.session_state:
    st.session_state["show_scan_uploader"] = False


# --- 🖼️ Load and Resize Banner ---
banner = Image.open("ibncare_banner.png")
resized_banner = banner.resize((1800, 600))  # Optimized for mobile view

st.markdown("""
    <style>
        html, body, .main {
            background-color: #cbe9e6;
        }
        section.main > div:first-child {
            padding-top: 0rem !important;
            margin-top: -4rem !important;
        }
        .block-container {
            padding-left: 2rem;
            padding-right: 2rem;
        }
        /* Expander Outer Box */
        div[data-testid="stExpander"] {
            background-color: #d0f0dc !important;
            border: 1px solid #a2d5c6 !important;
            border-radius: 10px;
            padding: 10px;
        }
        /* Expander Title Styling */
        div[data-testid="stExpander"] > summary {
           font-weight: 800 ;
           font-size: 18px ;
           color: #004d40 ;
           background-color: #d0f0dc;
           padding: 8px 12px;
           border-radius: 8px;
           font-family: 'Segoe UI', sans-serif ;
        }
        
        div[data-testid="stExpander"] > summary::before {
           content: "";
           text-shadow: 0 0 0 #000; /* This creates slight boldness illusion */
        }
        
        /* Input and text areas */
        input[type="text"], textarea {
            border: 1.5px solid #00796b !important;
            border-radius: 5px !important;
            padding: 8px !important;
            background-color: #ffffff;
        }
        .stNumberInput input {
            border: none !important;
        }
        .stNumberInput > div {
            border: 1.5px solid #00796b !important;
            border-radius: 5px !important;
            padding: 4px;
            background-color: #ffffff;
        }
        div[role="listbox"] {
            border: 1.5px solid #00796b !important;
            border-radius: 5px !important;
        }
        
        /* 🔥 Add THIS new block below your last rule */
        div[data-testid="stExpander"] + div[data-testid="stExpander"] {
            margin-top: -10px !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- 🖼️ Display Centered Banner ---
col1, col2, col3 = st.columns([0.2, 5.6, 0.2])
with col2:
    st.image(resized_banner)

# --- 🌼 Daily Inspiration Bar ---
affirmations = [
    "🌟 You are strong, capable, and healing every day.",
    "💪 Your health is your superpower — keep going!",
    "💚 Every small step you take is a step toward wellness.",
    "🌼 You are worthy of good health and happiness.",
    "☀️ Trust your body. Trust your journey.",
    "🧘‍♀️ Breathe in strength, breathe out stress.",
    "💖 Healing is not linear, but you are progressing beautifully.",
    "🌿 Your mind and body are working together in harmony.",
    "🌱 A healthy you means a healthier planet.",
    "🍀 Wellness grows when you nurture it—just like nature.",
    "🌸 Breathe clean, live clean, and keep the Earth green.",
    "💡 Choose kindness, to your body and to the Earth.",
]
selected_affirmation = random.choice(affirmations)

st.markdown(f"""
    <div style='
        background-color: #d0f0dc;
        padding: 12px 18px;
        border-radius: 10px;
        border: 1px solid #aad4bd;
        margin-top: -10px;
        margin-bottom: 5px;
        font-size: 15px;
        color: #1b4332;
        font-weight: 500;
        text-align: center;
        width: 100%;
        white-space: normal;
    '>
        🌼 <b>Daily Inspiration:</b> {selected_affirmation}
    </div>
""", unsafe_allow_html=True)


#---Chat Section--
with st.expander("**💬 Chat with IbnCare AI** ", expanded=False):
    st.markdown("<h6 style='color: #004d40; font-size: 15px; font-weight: 500;'>Let's get to know you:</h6>", unsafe_allow_html=True)

    # --- Top Row: Name + Clear Icon ---
    col1, col2 = st.columns([5, 1])
    with col1:
        st.session_state["user_name_chat"] = st.text_input(
            "👤 Enter your name:",
            placeholder="e.g., Ayesha",
            value=st.session_state["user_name_chat"]
        )
    with col2:
        st.markdown("<div style='padding-top: 25px;'>", unsafe_allow_html=True)
        if st.button("🧹", help="Clear Name, Gender, Age + Full Chat"):
            st.session_state["user_name_chat"] = ""
            st.session_state["gender_chat"] = "Select"
            st.session_state["age_chat"] = 0
            st.session_state["age_chat_key_suffix"] = ''.join(random.choices(string.ascii_letters, k=5))
            st.session_state["user_input"] = ""
            st.session_state["chat_response"] = ""
            st.session_state["chat_history"] = []
            st.success("✅ All Chat Data Cleared!")
            st.rerun()

    # --- Gender + Age ---
    gender_col, age_col = st.columns(2)
    gender_options = ["Select", "Male", "Female", "Other"]
    with gender_col:
        st.session_state["gender_chat"] = st.selectbox(
            "Select Gender:",
            gender_options,
            index=gender_options.index(st.session_state["gender_chat"]),
            key="gender_chat_box"
        )
    with age_col:
        age_key = f"age_chat_box_{st.session_state.get('age_chat_key_suffix', '')}"
        st.session_state["age_chat"] = st.number_input(
            "Enter Age:", min_value=0, max_value=120,
            value=st.session_state["age_chat"], step=1, key=age_key
        )

    # --- Chat Input ---
    st.markdown("<hr style='margin-top:10px;margin-bottom:5px;'>", unsafe_allow_html=True)
    st.markdown("<h6 style='color:#004d40; font-size: 15px; font-weight: 500;'>Ask your health-related question 👇</h6>", unsafe_allow_html=True)

    input_col1, input_col2, input_col3 = st.columns([5, 1, 1])
    with input_col1:
        chat_input_key = st.session_state.get("chat_input_box_key", "chat_input_box")
        st.session_state["user_input"] = st.text_input(
            "Ask your question:",
            placeholder="e.g., What is good relief for acidity?",
            value=st.session_state.get("user_input", ""),
            key=chat_input_key
        )

    with input_col2:
        st.markdown("<div style='padding-top: 25px;'>", unsafe_allow_html=True)
        lang_options = {"E": "en-US", "ع": "ar-SA"}
        selected_lang = st.selectbox("Select Language:", list(lang_options.keys()), index=0, label_visibility="collapsed")
    with input_col3:
        st.markdown("<div style='padding-top: 25px;'>", unsafe_allow_html=True)
        mic_clicked = st.button("🎤", help="Voice input supported")

    # --- Voice Input ---
    with input_col1:
        if mic_clicked:
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                mic_feedback = "<b>🎙 Listening...</b> Please speak clearly.<br>"
                try:
                    audio = recognizer.listen(source, timeout=10, phrase_time_limit=20)
                    query = recognizer.recognize_google(audio, language=lang_options[selected_lang])
                    st.session_state["user_input"] = query
                    mic_feedback += "✅ Voice captured: <i>{}</i>".format(query)
                except:
                    mic_feedback += "⚠️ Voice input failed."

            st.markdown(f"<div style='background-color:#e7f3fe; padding:12px; border-radius:10px;'>{mic_feedback}</div>", unsafe_allow_html=True)

    # ✅ Voice note repositioned just below mic icon + reduced gap before buttons
    mic_note = """
    <div style='font-size: 13px; color:#444; margin-top: -2px; margin-bottom: 1px;'>
        🌐 Supports <b>Arabic & English</b> voice input.
    </div>
    """
    st.markdown(mic_note, unsafe_allow_html=True)


    # --- Chat Buttons ---
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("Get Answer"):
            if st.session_state["user_input"]:
                response = requests.post(f"{BACKEND_URL}/chat", json={
                    "message": st.session_state["user_input"],
                    "user_name": st.session_state["user_name_chat"],
                    "gender": st.session_state["gender_chat"],
                    "age": st.session_state["age_chat"]
                })
                st.session_state["chat_response"] = response.json().get("response", "No response received.")
                if "chat_history" not in st.session_state:
                    st.session_state["chat_history"] = []
                st.session_state["chat_history"].append({
                    "user": st.session_state["user_input"],
                    "ai": st.session_state["chat_response"]
                })
            else:
                st.warning("Please enter a valid question.")
    with btn_col2:
        if st.button("🗑 Clear Chat History"):
            st.session_state["chat_response"] = ""
            st.session_state["chat_history"] = []
            st.session_state["user_input"] = ""
            st.session_state["chat_input_box_key"] = f"chat_input_box_{random.randint(1000, 9999)}"
            st.success("✅ Chat history cleared!")
            st.rerun()

    # --- Display Chat History ---
    if st.session_state.get("chat_history"):
        for entry in st.session_state["chat_history"]:
            st.markdown(f"**🤖 IbnCare AI:** {entry['ai']}")
            st.markdown("---")


# --- 📋 Log Day-to-Day Symptoms (Mobile-Friendly & Styled) ---
with st.expander("**📝 Day-to-Day Symptoms**", expanded=False):
    st.markdown("""<h6 style='color: #004d40; font-size: 15px; font-weight: 500;'>Log temporary issues like cold, pain, etc.</h6>""", unsafe_allow_html=True)

    sym_col1, sym_col2, sym_col3 = st.columns([1.5, 1, 1])
    with sym_col1:
        st.session_state["user_name_symptom"] = st.text_input("Name:", value=st.session_state["user_name_symptom"])
    with sym_col2:
        st.session_state["gender_symptom"] = st.selectbox(
            "Gender:", gender_options,
            index=gender_options.index(st.session_state["gender_symptom"]),
            key="gender_symptom_box"
        )
    with sym_col3:
        age_symptom_key = st.session_state.get("age_symptom_key", "age_symptom_box")
        st.session_state["age_symptom"] = st.number_input(
            "Age:", min_value=1, max_value=120,
            value=st.session_state["age_symptom"] or 30,
            step=1, key=age_symptom_key
        )

    # ✅ Fix applied here using a dynamic key
    symptom_input_key = st.session_state.get("symptom_input_key", "symptom_input_box")
    st.session_state["symptom_input"] = st.text_input(
        "Describe your symptom:",
        value=st.session_state["symptom_input"],
        key=symptom_input_key
    )

    col3, col4 = st.columns([1, 1])
    with col3:
        if st.button("Log Symptom"):
            if all([
                st.session_state["user_name_symptom"],
                st.session_state["symptom_input"],
                st.session_state["gender_symptom"] != "Select"
            ]):
                res = requests.post(f"{BACKEND_URL}/log_symptom", json={
                    "user_name": st.session_state["user_name_symptom"],
                    "gender": st.session_state["gender_symptom"],
                    "age": st.session_state["age_symptom"],
                    "symptom": st.session_state["symptom_input"]
                })
                if res.status_code == 200:
                    st.success("✅ Symptom logged!")

                    # Optional: auto-analysis
                    symptom_check = requests.post(f"{BACKEND_URL}/get_symptoms", json={
                        "user_name": st.session_state["user_name_symptom"]
                    })

                    if symptom_check.status_code == 200:
                        data = symptom_check.json()
                        recent_symptoms = data.get("logged_symptoms", [])
                        if len(recent_symptoms) >= 7:
                            st.info("🔍 7 symptoms logged. Analyzing now...")
                            analysis_res = requests.post(f"{BACKEND_URL}/analyze_symptoms", json={
                                "user_name": st.session_state["user_name_symptom"]
                            })
                            if analysis_res.status_code == 200:
                                analysis_data = analysis_res.json()
                                st.success("✅ AI Symptom Analysis")
                                st.write("### Analysis Result:")
                                st.write(analysis_data.get("analysis", "No analysis result received."))
                            else:
                                st.warning("⚠️ Symptom analysis failed. Please try again.")
                else:
                    st.error("❌ Failed to log symptom.")
            else:
                st.warning("Please complete all fields.")

    with col4:
        if st.button("🧹 Clear Symptom Form"):
            for key in ["user_name_symptom", "gender_symptom", "age_symptom", "symptom_input"]:
                st.session_state[key] = defaults[key]
            # 👇 Force UI reset by changing keys
            st.session_state["symptom_input_key"] = f"symptom_input_box_{random.randint(1000, 9999)}"
            st.session_state["age_symptom_key"] = f"age_symptom_box_{random.randint(1000, 9999)}"
            st.success("✅ Cleared symptom form!")
            st.rerun()

    st.markdown("<hr style='margin-top:25px;margin-bottom:15px;'>", unsafe_allow_html=True)
    st.markdown("<h6 style='color:#004d40; font-size: 15px; font-weight: 500;'>📜 View Past Symptoms & Manual Analysis</h6>", unsafe_allow_html=True)

    col5, col6 = st.columns([1, 1])
    with col5:
        if st.button("📄 View My Symptoms"):
            if st.session_state["user_name_symptom"] and st.session_state["gender_symptom"] != "Select":
                symptom_history_response = requests.post(f"{BACKEND_URL}/get_symptoms", json={
                    "user_name": st.session_state["user_name_symptom"],
                    "gender": st.session_state["gender_symptom"],
                    "age": st.session_state["age_symptom"]
                })
                symptoms_data = symptom_history_response.json()
                if "logged_symptoms" in symptoms_data:
                    st.write("### Your Past Symptoms:")
                    for entry in symptoms_data["logged_symptoms"]:
                        st.write(f"📅 {entry['date']} - **{entry['symptom']}**")
                else:
                    st.warning(symptoms_data.get("message", "No symptom records found."))
            else:
                st.warning("Please fill in your Name, Gender, and Age before viewing symptoms.")

    with col6:
        if st.button("📊 Analyze Manually"):
            if st.session_state["user_name_symptom"] and st.session_state["gender_symptom"] != "Select":
                analysis_response = requests.post(f"{BACKEND_URL}/analyze_symptoms", json={
                    "user_name": st.session_state["user_name_symptom"],
                    "gender": st.session_state["gender_symptom"],
                    "age": st.session_state["age_symptom"]
                })
                if analysis_response.status_code == 200:
                    analysis_result = analysis_response.json()
                    st.success("✅ Symptom analysis completed!")
                    if "analysis" in analysis_result:
                        st.write("**AI Analysis:**", analysis_result["analysis"])
                    else:
                        st.warning("No analysis message returned.")
                else:
                    st.error("❌ Failed to analyze symptoms.")
            else:
                st.warning("Please fill in your Name, Gender, and Age before analyzing.")

# --- 📋 Chronic Medical Conditions (Mobile-Friendly & Styled) ---
with st.expander("**📋 Chronic Medical Conditions**", expanded=False):
    st.markdown("""<h6 style='color: #004d40; font-size: 15px; font-weight: 500;'>Add long-term conditions (e.g., diabetes, surgery)</h6>""", unsafe_allow_html=True)

    # Name, Gender, Age row
    med_col1, med_col2, med_col3 = st.columns([1.5, 1, 1])
    with med_col1:
        st.session_state["medical_user_name"] = st.text_input(
            "Name:", value=st.session_state["medical_user_name"], key="medical_user_name_input"
        )
    with med_col2:
        st.session_state["gender_medical"] = st.selectbox(
            "Gender:", gender_options,
            index=gender_options.index(st.session_state["gender_medical"]),
            key="gender_medical_box"
        )
    with med_col3:
        age_medical_key = st.session_state.get("age_medical_key", "age_medical_box")
        st.session_state["age_medical"] = st.number_input(
            "Age:", min_value=1, max_value=120,
            value=st.session_state["age_medical"] or 30,
            step=1, key=age_medical_key
        )

    # Condition Type and Description
    condition_type_key = st.session_state.get("condition_type_key", "condition_type_input")
    st.session_state["condition_type"] = st.text_input(
        "Condition Type:", value=st.session_state["condition_type"], key=condition_type_key
    )

    condition_desc_key = st.session_state.get("condition_desc_key", "condition_desc_input")
    st.session_state["condition_description"] = st.text_area(
        "Condition Description:", value=st.session_state["condition_description"], key=condition_desc_key
    )

    # Submit + Clear
    col7, col8 = st.columns([1, 1])
    with col7:
        if st.button("Submit Medical History"):
            if st.session_state["medical_user_name"] and st.session_state["condition_type"] and st.session_state["gender_medical"] != "Select":
                res = requests.post(f"{BACKEND_URL}/log_medical_history", json={
                    "medical_user_name": st.session_state["medical_user_name"],
                    "gender": st.session_state["gender_medical"],
                    "age": st.session_state["age_medical"],
                    "condition_type": st.session_state["condition_type"],
                    "condition_description": st.session_state["condition_description"]
                })
                if res.status_code == 200:
                    st.success("✅ Medical history submitted!")
                else:
                    st.error("❌ Failed to submit medical history.")
            else:
                st.warning("Please complete all fields.")

    with col8:
        if st.button("🧹 Clear Medical Form"):
            for key in ["medical_user_name", "gender_medical", "age_medical", "condition_type", "condition_description"]:
                st.session_state[key] = defaults[key]
            st.session_state["condition_type_key"] = f"condition_type_input_{random.randint(1000,9999)}"
            st.session_state["condition_desc_key"] = f"condition_desc_input_{random.randint(1000,9999)}"
            st.session_state["age_medical_key"] = f"age_medical_box_{random.randint(1000,9999)}"
            st.success("✅ Cleared medical form!")
            st.rerun()

    # View and Clear
    st.markdown("<hr style='margin-top:25px;margin-bottom:15px;'>", unsafe_allow_html=True)
    st.markdown("<h6 style='color:#004d40; font-size: 15px; font-weight: 500;'>📖 View Medical History</h6>", unsafe_allow_html=True)

    col9, col10 = st.columns([1, 1])
    with col9:
        if st.button("📄 View Medical History"):
            if st.session_state["medical_user_name"] and st.session_state["gender_medical"] != "Select" and st.session_state["age_medical"]:
                res = requests.post(f"{BACKEND_URL}/get_medical_history", json={
                    "medical_user_name": st.session_state["medical_user_name"],
                    "gender": st.session_state["gender_medical"],
                    "age": st.session_state["age_medical"]
                })
                data = res.json()
                if "medical_history" in data:
                    st.session_state["medical_history_data"] = data["medical_history"]
                    st.success("✅ Medical history retrieved!")
                else:
                    st.session_state["medical_history_data"] = []
                    st.warning(data.get("message", "No medical history found."))
            else:
                st.warning("Please fill in your Name, Gender, and Age to view history.")

    with col10:
        if st.button("🗑 Clear Medical Retrieval"):
            st.session_state["medical_user_name"] = ""
            st.session_state["medical_history_data"] = []
            st.success("✅ Cleared medical history input.")
            st.rerun()

    if st.session_state.get("medical_history_data"):
        st.write("### Your Medical History:")
        for entry in st.session_state["medical_history_data"]:
            st.write(f"🩺 **Condition Type:** {entry['condition_type']}")
            st.write(f"📝 **Description:** {entry['condition_description']}")
            st.write(f"📅 **Date:** {entry['date']}")
            st.markdown("---")


# --- 📤 Export PDF (Aligned, Mobile-friendly)
pdf_row = st.columns([0.08, 0.92])
with pdf_row[0]:
    export_pdf_clicked = st.button("📄", key="generate_pdf", help="Generate PDF summary")
with pdf_row[1]:
    st.markdown(
        """
        <span style='font-weight: bold; font-size: 15px; color: #1b5e20;'>Export PDF</span>
        <br>
        <span style='font-size: 12px; color: #555;'>Fill Name, Gender & Age in chat section. If your data exists, it will be exported.</span>
        """, unsafe_allow_html=True
    )

# --- Export Logic
if export_pdf_clicked:
    user_name = st.session_state.get("user_name_chat", "").strip()
    gender = st.session_state.get("gender_chat", "").strip()
    age = st.session_state.get("age_chat", 0)

    if not user_name or gender == "Select" or not age:
        st.warning("⚠️ Please fill in your Name, Gender & Age before exporting.")
    else:
        try:
            symptom_res = requests.post(f"{BACKEND_URL}/get_symptoms", json={
                "user_name": user_name, "gender": gender, "age": age
            })
            medical_res = requests.post(f"{BACKEND_URL}/get_medical_history", json={
                "medical_user_name": user_name, "gender": gender, "age": age
            })

            symptoms_data = symptom_res.json() if symptom_res.status_code == 200 else {}
            medical_data = medical_res.json() if medical_res.status_code == 200 else {}
            symptoms = symptoms_data.get("logged_symptoms", [])
            medical_history = medical_data.get("medical_history", [])
            chat_history = st.session_state.get("chat_history", [])

            if not symptoms and not medical_history:
                st.warning("❌ No data found in Symptoms or Medical History.")
            else:
                payload = {
                    "user_name": user_name,
                    "gender": gender,
                    "age": age,
                    "chat_history": [{"question": h["user"], "response": h["ai"]} for h in chat_history],
                    "symptoms": symptoms,
                    "medical_history": medical_history
                }
                res = requests.post(f"{BACKEND_URL}/export_pdf", json=payload)
                if res.status_code == 200:
                    file_path = f"{user_name}_health_summary.pdf"
                    with open(file_path, "wb") as f:
                        f.write(res.content)
                    st.success("✅ PDF exported successfully!")
                    with open(file_path, "rb") as pdf_file:
                        st.download_button("📥 Download PDF", data=pdf_file.read(), file_name=file_path, mime="application/pdf")
                    os.remove(file_path)
                else:
                    st.error("❌ PDF export failed.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# --- 📑 Upload Scan (Aligned, Compact)
scan_row = st.columns([0.08, 0.92])
with scan_row[0]:
    scan_clicked = st.button("📤", key="scan_upload_icon", help="Upload scan report")
    if scan_clicked:
        st.session_state["show_scan_uploader"] = True

with scan_row[1]:
    st.markdown(
        """
        <span style='font-weight: bold; font-size: 15px; color: #1b5e20;'>Upload Medical Scan Report</span>
        <br>
        <span style='font-size: 12px; color: #555;'>PNG, JPG, JPEG supported. 📄 PDF support coming soon. Limit: 200MB.</span>
        """, unsafe_allow_html=True
    )

# --- Uploader logic
if st.session_state.get("show_scan_uploader", False):
    uploaded_file = st.file_uploader("Choose scan image or PDF", type=["png", "jpg", "jpeg", "pdf"], key="scan_file_uploader")
    if uploaded_file:
        with st.spinner("🧠 Analyzing scan report..."):
            try:
                res = requests.post(f"{BACKEND_URL}/upload_scan", files={"file": (uploaded_file.name, uploaded_file, uploaded_file.type)})
                if res.status_code == 200:
                    data = res.json()
                    st.success("✅ Scan uploaded and analyzed!")
                    with st.expander("📜 Extracted Text (OCR)"):
                        st.text_area("Extracted Text:", value=data.get("extracted_text", ""), height=150)
                    with st.expander("🧠 AI Explanation"):
                        st.markdown(data.get("summary", "No summary available."))
                    st.session_state["show_scan_uploader"] = False
                else:
                    st.error("❌ Failed to analyze scan.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
