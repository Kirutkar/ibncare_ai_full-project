🩺 IbnCare AI – Your Personal Health & Wellness Assistant

IbnCare AI is a thoughtful AI-powered health assistant designed to provide gentle health support, symptom tracking, and emotional reassurance. It enables users to chat about their health, log symptoms, manage chronic conditions, and export a personal health summary—all within a clean, mobile-friendly interface.

🌟 Key Features

🤖 Chatbot: Supports both English and Arabic languages.

📝 Log Daily Symptoms: Keep track of your daily health status.

🩺 Track Chronic Conditions: Monitor ongoing health issues.

📑 Upload Medical Reports: Accepts image files (.jpeg, .jpg, .png).

📤 Export PDF Health Summary: Generate a comprehensive health report.

🧘 Daily Affirmations: Receive daily mental wellness tips.

🗂️ Project Structure

ibncare_ai_local/

├── app_backend.py        # Flask backend handling API routes

├── app_frontend.py       # Streamlit frontend for user interaction

├── utils.py              # Utility functions for image processing

├── ibncare_banner.png    # UI banner image for branding

├── requirements.txt      # Python dependencies

├── .env.example          # Example environment variables file

└── README.md             # Project documentation

⚙️ Local Setup Instructions

1. 📁 Environment Variables Setup
   
Create a .env file in the root directory with the following content:

GOOGLE_API_KEY=your_google_api_key

# PostgreSQL Database Configuration

PG_HOST=your_host

PG_USER=your_user

PG_PASSWORD=your_password

PG_DATABASE=your_database

⚠️ Note: Voice input is not supported in this version due to PyAudio limitations. This local version supports text input in both Arabic and English.

2. 🧪 Install Python Dependencies
   
Install all required Python packages using:

pip install -r requirements.txt

3. 🧠 Run the Application Locally
   
Start the Flask backend:

python app_backend.py

In a separate terminal, launch the Streamlit frontend:

streamlit run app_frontend.py

🗒️ Additional Notes

This project is designed to run fully on local systems.

Voice input is not supported in this version due to PyAudio limitations.

The scan upload feature (OCR + AI summary) works for .jpeg, .jpg, and .png formats. PDF support is not available at this time.

Future enhancements planned:

Add a date of birth field (instead of age) for consistent tracking.

Generate unique User IDs for better user management.

🚀 What's Unique?

A gentle, human-centered approach to health.

Bilingual chatbot supporting Arabic and English.

Thoughtful logic for symptoms, medical history, and personalization.

Simple scan upload feature with AI-generated explanations.

Export-ready health summary for personal use or doctor visits.

📷 Sneak Peek

![image](https://github.com/user-attachments/assets/0a28fee7-5671-4b10-8233-64879978a880)


🧠 Final Thoughts

This project was built with care and simplicity in mind—no advanced NLP libraries or ML models used. It leverages the Google Gemini API and practical healthcare flows to provide a supportive experience. It's designed to feel like a helpful friend in your pocket 💚

👩‍💻 Author

Built by: Kiruthika Ramalingam

For: AI Application Challenge 2025 – Final Submission

Project Goal: Help users feel seen, cared for, and supported.
