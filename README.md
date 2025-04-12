# ibncare_ai_full-project
**IbnCare AI** is a simple yet thoughtful AI-powered health assistant built to provide gentle health support, symptom tracking, and emotional reassurance. It allows users to chat about their health, log symptoms, manage chronic conditions, and export a personal health summary – all in a clean, mobile-friendly interface.

## 🌟 Key Features

- 🤖 Chatbot (English + Arabic support)
- 📝 Log Daily Symptoms
- 🩺 Track Chronic Conditions
- 📑 Upload Medical Reports (Image files like jpeg,jpg or png)
- 📤 Export PDF Health Summary
- 🧘 Daily Affirmations for mental wellness

---


ibncare_ai_local/

├── app_backend.py

├── app_frontend.py

├── utils.py

├── ibncare_banner.png

├── requirements.txt

├── .env.example

└── README.md



## ⚙️ Local Setup Instructions

### 1. 📁 `.env` Setup

Create a `.env` file with the following:

GOOGLE_API_KEY=your_google_api_key

Neon/PostgreSQL Database

PG_HOST=your_host

PG_USER=your_user

PG_PASSWORD=your_password

PG_DATABASE=your_db 

> ⚠️ **Voice Input not supported in this version due to PyAudio limitations.** This local version supports text input (Arabic + English).

---
2. 🧪 Install Dependencies

Install all required Python packages using:

pip install -r requirements.txt


3. 🧠 Run the App

# Start the Flask Backend

python app_backend.py

# In a separate terminal, launch the Streamlit Frontend

streamlit run app.py

## 🗒️ Notes

- This project runs fully on local systems.
- For deployment, voice input is not supported (due to PyAudio limitations on Render).
- Voice input works perfectly on local installations. Just run the app and speak in English or Arabic!
- Scan upload (OCR + AI summary) works for jpeg,jpg,png format,doesn't support pdf for time being.
- In future versions, we plan to:
  - Add a date of birth field (instead of age) for consistent tracking.
  - Generate unique User IDs.
 
🚀 What's Unique?

A gentle, human-centered approach to health

Arabic + English input chatbot replies

Thoughtful logic for symptoms + medical history + personalization

Simple scan upload feature with AI explanation

Export-ready health summary for personal use or doctor visits


📷 Sneak Peek

![image](https://github.com/user-attachments/assets/0a28fee7-5671-4b10-8233-64879978a880)


🧠 Note

This project was built with care and simplicity in mind – no advanced NLP libraries or ML models used, only thoughtful use of Google Gemini API and practical healthcare flows. It's designed to feel like a helpful friend in your pocket 💚

👩‍💻 Author

Built by:Kiruthika Ramalingam

For: AI Application Challenge 2025 – Final Submission

Project Goal: Help users feel seen, cared for, and supported.



