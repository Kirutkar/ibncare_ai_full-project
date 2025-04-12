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

✅ This project works entirely on local machines.

❌ Voice input is disabled in deployment (due to PyAudio + Render compatibility).

✅ Voice input works perfectly in local environments (supports English & Arabic).

📑 Scan Upload supports JPG, JPEG, PNG only – PDF support is coming soon.

🧭 Future Plans

Replace age with date of birth for consistent tracking

Generate unique user IDs for better health history management

🚀 What Makes It Unique?

💚 A gentle, human-centered approach to health

🌐 Arabic + English chatbot support

🧠 Smart logic based on symptom history + conditions

📤 Exportable health summary for doctor visits

📑 Scan upload with simplified AI explanation




📷 Sneak Peek

![image](https://github.com/user-attachments/assets/0a28fee7-5671-4b10-8233-64879978a880)


🧠 Note

This project was built with care and simplicity in mind – no advanced NLP libraries or ML models used, only thoughtful use of Google Gemini API and practical healthcare flows. It's designed to feel like a helpful friend in your pocket 💚

👩‍💻 Author

Built by:Kiruthika Ramalingam

For: AI Application Challenge 2025 – Final Submission

Project Goal: Help users feel seen, cared for, and supported.



