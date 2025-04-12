import os
import google.generativeai as genai
from dotenv import load_dotenv
from fpdf import FPDF
from flask import send_file
import tempfile
from flask import Flask, request, jsonify
import pytesseract
from PIL import Image
import io
import google.generativeai as genai
from flask_cors import CORS
import fitz
from pdf2image import convert_from_path

POPPLER_PATH = r'C:\poppler-21.02.0\Library\bin'
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'



# --- Load environment variables ---
load_dotenv()

# Ensure API key is present
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("❌ Error: GOOGLE_API_KEY is missing. Please check your .env file.")

genai.configure(api_key=api_key)



app = Flask(__name__)
CORS(app)  # Enable CORS

# --- Global cache dictionary to store previous responses ---
cache = {}

import psycopg2
import psycopg2.extras  # ✅ ADD THIS LINE




def connect_db():
    try:
        conn = psycopg2.connect(
            host=os.getenv("PG_HOST"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            database=os.getenv("PG_DATABASE"),
            port=os.getenv("PG_PORT", 5432),
            sslmode='require'  # Neon requires SSL
        )
        return conn
    except Exception as e:
        print(f"❌ PostgreSQL Connection Error: {e}")
        return None

from langdetect import detect
from googletrans import Translator

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()

    if not data or "message" not in data or "user_name" not in data or "gender" not in data or "age" not in data:
        return jsonify({"error": "Please provide message, user_name, gender, and age."}), 400

    user_message = data["message"]
    user_name = data["user_name"].strip().lower()
    gender = data["gender"].strip().lower()
    age = str(data["age"])

    # --- Language Detection ---
    translator = Translator()
    is_arabic = detect(user_message) == "ar"

    translated_input = user_message
    if is_arabic:
        try:
            translated_input = translator.translate(user_message, src='ar', dest='en').text
        except Exception as e:
            return jsonify({"response": f"Translation error: {str(e)}"}), 500

    user_msg_lower = translated_input.strip().lower()

    # --- DB fetch ---
    conn = connect_db()
    if conn is None:
        return jsonify({"error": "Database connection failed."}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("""SELECT symptom FROM symptoms 
                          WHERE LOWER(TRIM(user_name)) = %s AND LOWER(TRIM(gender)) = %s AND age = %s 
                          AND timestamp >=  CURRENT_DATE - INTERVAL '10 days' ORDER BY timestamp DESC""",
                       (user_name, gender, age))
        symptom_rows = cursor.fetchall()
        recent_symptoms = [row[0] for row in symptom_rows if row[0].strip().lower() != user_msg_lower]

        cursor.execute("""SELECT condition_type FROM medical_history 
                          WHERE LOWER(TRIM(medical_user_name)) = %s AND LOWER(TRIM(gender)) = %s AND age = %s
                          ORDER BY created_at DESC""",
                       (user_name, gender, age))
        med_rows = cursor.fetchall()
        medical_conditions = [row[0] for row in med_rows]
    except psycopg2.Error as err:
        return jsonify({"error": f"Database error: {err}"}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

    # --- Logic same as before ---
    new_user_disclaimer = ""
    if not recent_symptoms and not medical_conditions:
        new_user_disclaimer = (
            "🧾 *Note: No recent symptoms or medical history found for this user.*\n"
            "📌 This advice is based only on your current message. For personalized care, try logging your symptoms or medical history.\n\n"
        )

    # Keyword checks
    diet_keywords = ["diet", "meal plan", "recipes", "nutrition", "food", "healthy eating"]
    meal_keywords = ["breakfast", "lunch", "dinner", "menu", "full-day", "full plan", "one day", "three meals"]
    symptom_keywords = ["symptom", "pain", "discomfort", "ache", "stomach", "bloating", "headache", "vomit",
                        "nausea", "gas", "cold", "fever", "urination", "itch", "infection", "skin", "rash"]
    remedy_keywords = ["remedy", "cure", "medicine", "treatment", "soothe", "relieve", "manage"]
    fear_keywords = ["scared", "anxious", "nervous", "fear", "panic", "heart attack"]

    is_diet_query = any(k in user_msg_lower for k in diet_keywords)
    is_full_meal_request = any(k in user_msg_lower for k in meal_keywords)
    is_symptom_or_pain = any(k in user_msg_lower for k in symptom_keywords)
    is_remedy_related = any(k in user_msg_lower for k in remedy_keywords)
    is_fear_or_emergency = any(k in user_msg_lower for k in fear_keywords)

    is_health_related = is_diet_query or is_full_meal_request or is_symptom_or_pain or is_remedy_related or is_fear_or_emergency
    if not is_health_related:
        return jsonify({"response": "🙏 I'm here to support your health. Please ask something related to symptoms, remedies, or diet. 💚"})

    # Prompt build
    health_context = f"The user is a {age}-year-old {gender} named {user_name}. "
    if medical_conditions:
        health_context += f"They have medical history of: {', '.join(medical_conditions)}. "
    if recent_symptoms:
        health_context += f"In the last 10 days, they experienced symptoms like: {', '.join(recent_symptoms)}. "

    if is_diet_query and is_full_meal_request:
        prompt = (
            f"You are a certified nutritionist. 🍎🥗\n\nCreate a 1-day meal plan for:\n"
            f"- Age: {age}, Gender: {gender}\nMedical History: {', '.join(medical_conditions) or 'None'}\n"
            f"Symptoms: {', '.join(recent_symptoms) or 'None'}\n\n"
            f"**Breakfast:**\n**Lunch:**\n**Dinner:**\n"
        )
    elif is_diet_query:
        prompt = f"List 3–5 healthy foods for a {age}-year-old {gender} with conditions: {', '.join(medical_conditions)}."
    elif is_symptom_or_pain or is_remedy_related:
        prompt = f"{health_context}\nUser reported: {translated_input}\nSuggest causes + 2 home remedies in a kind tone."
    elif is_fear_or_emergency:
        prompt = f"{health_context}\nUser seems anxious: {translated_input}\nRespond gently and reassure them with 2 calming tips."
    else:
        prompt = f"{health_context}\nUser asked: {translated_input}\nReply simply and kindly."

    # Gemini
    try:
        cache_key = f"{user_name}_{user_msg_lower}"
        if cache_key in cache:
            final_response = cache[cache_key]
        else:
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content([prompt, translated_input])
            final_response = response.candidates[0].content.parts[0].text.strip()
            cache[cache_key] = final_response

        if is_arabic:
            final_response = translator.translate(final_response, src='en', dest='ar').text

        return jsonify({"response": new_user_disclaimer + final_response})

    except Exception as e:
        return jsonify({"response": f"❌ AI Error: {str(e)}"})



@app.route("/log_symptom", methods=["POST"])
def log_symptom():
    data = request.get_json()

    if not data or "user_name" not in data or "symptom" not in data or "gender" not in data or "age" not in data:
        return jsonify({"error": "Invalid input. Please provide user_name, symptom, gender, and age."}), 400

    user_name = data["user_name"]
    symptom = data["symptom"]
    gender = data["gender"]
    age = str(data["age"])

    conn = connect_db()
    if conn is None:
        return jsonify({"error": "Database connection failed."}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO symptoms (user_name, symptom, gender, age) VALUES (%s, %s, %s, %s)",
                       (user_name, symptom, gender, age))
        conn.commit()

        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # --- Analyze symptoms if we have 7 days of logs ---
        
        cursor.execute("""
            SELECT symptom, gender, age 
            FROM symptoms 
            WHERE LOWER(TRIM(user_name)) = %s 
              AND timestamp >= CURRENT_DATE - INTERVAL '7 days'
            ORDER BY timestamp DESC
        """, (user_name.lower(),))
        rows = cursor.fetchall()

        if len(rows) >= 7:
            symptoms = [row["symptom"] for row in rows]
            gender = rows[0].get("gender", "unknown")
            age = rows[0].get("age", "unknown")

            symptom_list = "\n".join([f"- {s}" for s in symptoms])
            prompt = (
                f"You are a medical assistant. A {gender.lower()} aged {age} has reported the following symptoms over the last 7 days:\n"
                f"{symptom_list}\n\n"
                "1. Analyze the seriousness based on symptom combination and age/gender.\n"
                "2. If it's mild/common, provide a reassuring, friendly message.\n"
                "3. If it’s serious or persistent, suggest consulting a doctor politely.\n"
                "Keep it short and empathetic (max 4–6 lines)."
            )

            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content([prompt, "Please analyze the symptoms."])
            if response.candidates and response.candidates[0].content.parts:
                analysis_message = response.candidates[0].content.parts[0].text.strip()
            else:
                analysis_message = "Sorry, I couldn't analyze your symptoms right now."

            return jsonify({
                "message": "Symptom logged successfully!",
                "analysis": analysis_message
            })

        else:
            return jsonify({"message": "Symptom logged successfully! (Not enough data for analysis yet.)"})

    except psycopg2.Error as err:
        return jsonify({"error": f"Database error: {err}"}), 500
    except Exception as e:
        return jsonify({"error": f"Gemini error: {str(e)}"}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@app.route("/get_symptoms", methods=["POST"])
def get_symptoms():
    data = request.get_json()

    if not data or "user_name" not in data or "gender" not in data or "age" not in data:
        return jsonify({"error": "Please provide user_name, gender, and age."}), 400

    user_name = data["user_name"].strip().lower()
    gender = data["gender"].strip().lower()
    age = str(data["age"])

    conn = connect_db()
    if conn is None:
        return jsonify({"error": "Database connection failed."}), 500

    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # 🔍 Optional Debugging (Can remove in production)
        cursor.execute("SELECT DISTINCT LOWER(user_name), gender, age FROM symptoms;")
        print("DEBUG: All users in DB -", cursor.fetchall())

        # ✅ Fetch symptoms using name + gender + age
        cursor.execute("""
            SELECT symptom, timestamp FROM symptoms 
            WHERE LOWER(TRIM(user_name)) = %s AND LOWER(TRIM(gender)) = %s AND age = %s
            ORDER BY timestamp DESC
        """, (user_name, gender, age))
        symptoms = cursor.fetchall()

        if not symptoms:
            return jsonify({"message": f"No symptoms found for user: {user_name} ({gender}, {age})."})

        symptom_list = [{"symptom": row["symptom"], "date": row["timestamp"].strftime('%Y-%m-%d')} for row in symptoms]
        return jsonify({"user": user_name, "logged_symptoms": symptom_list})

    except psycopg2.Error as err:
        print(f"❌ Database Error: {err}")
        return jsonify({"error": f"Database error: {err}"}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@app.route("/log_medical_history", methods=["POST"])
def log_medical_history():
    data = request.get_json()

    if not data or "medical_user_name" not in data or "condition_type" not in data or "gender" not in data or "age" not in data:
        return jsonify({"error": "Invalid input. 'medical_user_name', 'condition_type', 'gender', and 'age' required."}), 400

    user_name = data["medical_user_name"]
    condition_type = data["condition_type"]
    description = data.get("condition_description", "")
    gender = data["gender"]
    age =str(data["age"])

    conn = connect_db()
    if conn is None:
        return jsonify({"error": "Database connection failed."}), 500

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO medical_history (medical_user_name, condition_type, condition_description, gender, age)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (user_name, condition_type, description, gender, age)
        )
        conn.commit()
        return jsonify({"message": "Medical history recorded successfully!"})

    except psycopg2.Error as err:
        print(f"❌ PostgreSQL Error: {err}")
        return jsonify({"error": f"Database error: {err}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

import psycopg2  # ensure this is imported if not already

@app.route("/get_medical_history", methods=["POST"])
def get_medical_history():
    data = request.get_json()

    if not all(k in data for k in ("medical_user_name", "gender", "age")):
        return jsonify({"error": "Invalid request. 'medical_user_name', 'gender', and 'age' are required."}), 400

    medical_user_name = data["medical_user_name"].strip().lower()
    gender = data["gender"].strip().lower()
    age = str(data["age"])

    conn = connect_db()
    if conn is None:
        return jsonify({"error": "Database connection failed."}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT condition_type, condition_description, created_at 
            FROM medical_history 
            WHERE LOWER(TRIM(medical_user_name)) = %s AND LOWER(TRIM(gender)) = %s AND age = %s
            ORDER BY created_at DESC
        """, (medical_user_name, gender, age))
        records = cursor.fetchall()

        if not records:
            return jsonify({"message": "No medical history found for this user."})

        result = [{"condition_type": r[0], "condition_description": r[1], "date": r[2].strftime('%Y-%m-%d')} for r in records]
        return jsonify({"user": medical_user_name, "medical_history": result})

    except psycopg2.Error as err:
        print(f"❌ PostgreSQL Error: {err}")
        return jsonify({"error": f"Database error: {err}"}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@app.route("/analyze_symptoms", methods=["POST"])
def analyze_symptoms():
    data = request.get_json()

    if not all(k in data for k in ("user_name", "gender", "age")):
        return jsonify({"error": "Missing user_name, gender, or age"}), 400

    user_name = data["user_name"].strip().lower()
    gender = data["gender"].strip().lower()
    age =str(data["age"])

    conn = connect_db()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT symptom 
            FROM symptoms 
            WHERE LOWER(TRIM(user_name)) = %s AND LOWER(TRIM(gender)) = %s AND age = %s 
              AND timestamp >= CURRENT_DATE - INTERVAL '7 days'
            ORDER BY timestamp DESC
        """, (user_name, gender, age))
        rows = cursor.fetchall()

        if not rows:
            return jsonify({"message": "No symptoms found for this user."})

        symptoms = [row[0] for row in rows]

        symptom_list = "\n".join([f"- {s}" for s in symptoms])
        prompt = (
            f"You are a medical assistant. A {gender.lower()} aged {age} has reported the following symptoms over the last 7 days:\n"
            f"{symptom_list}\n\n"
            "1. Analyze the seriousness based on symptom combination and age/gender.\n"
            "2. If it's mild/common, provide a reassuring, friendly message.\n"
            "3. If it’s serious or persistent, suggest consulting a doctor politely.\n"
            "Keep it short and empathetic (max 4–6 lines)."
        )

        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content([prompt, "Please provide your analysis."])

        if response.candidates and response.candidates[0].content.parts:
            message = response.candidates[0].content.parts[0].text.strip()
        else:
            message = "Sorry, I couldn't analyze your symptoms at the moment. Please try again later."

        return jsonify({
            "user": user_name,
            "symptoms": symptoms,
            "gender": gender,
            "age": age,
            "analysis": message
        })

    except psycopg2.Error as err:
        print(f"❌ PostgreSQL Error: {err}")
        return jsonify({"error": f"Database error: {err}"}), 500
    except Exception as e:
        return jsonify({"error": f"Gemini error: {str(e)}"}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@app.route("/export_pdf", methods=["POST"])
def export_pdf():
    data = request.get_json()

    required_fields = ["user_name", "gender", "age", "chat_history", "symptoms", "medical_history"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields in request."}), 400

    user_name = data["user_name"]
    gender = data["gender"]
    age = str(data["age"])
    chat_history = data["chat_history"]
    symptoms = data["symptoms"]
    medical_history = data["medical_history"]

    def safe_text(text):
        return str(text).encode("latin-1", errors="ignore").decode("latin-1")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=safe_text("AI Health Summary"), ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=safe_text(f"Name: {user_name} | Gender: {gender} | Age: {age}"), ln=True)

    # Chat History
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Chat History:", ln=True)
    pdf.set_font("Arial", size=12)
    for item in chat_history:
        pdf.multi_cell(0, 10, safe_text(f"Q: {item['question']}\nA: {item['response']}"))
        pdf.ln(2)

    # Symptoms
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Logged Symptoms:", ln=True)
    pdf.set_font("Arial", size=12)
    for s in symptoms:
        pdf.cell(200, 10, txt=safe_text(f"- {s['symptom']} ({s['date']})"), ln=True)

    # Medical History
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Medical History:", ln=True)
    pdf.set_font("Arial", size=12)
    for m in medical_history:
        pdf.multi_cell(0, 10, safe_text(f"- {m['condition_type']}: {m['condition_description']} ({m['date']})"))
        pdf.ln(1)

    # Save to a temp file and return
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        pdf.output(tmp_file.name)
        tmp_file.flush()
        return send_file(tmp_file.name, as_attachment=True, download_name=f"{user_name}_health_summary.pdf")


from utils import preprocess  # make sure utils.py is in same folder

@app.route("/upload_scan", methods=["POST"])
def upload_scan():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    filename = file.filename.lower()
    extracted_text = ""

    try:
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            image = Image.open(file.stream)
            processed = preprocess(image)
            extracted_text = pytesseract.image_to_string(Image.fromarray(processed))

        elif filename.endswith('.pdf'):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                tmp_pdf.write(file.read())
                tmp_pdf_path = tmp_pdf.name

            try:
                images = convert_from_path(tmp_pdf_path, poppler_path=POPPLER_PATH)

                if not images or len(images) == 0:
                    return jsonify({"error": "❌ PDF loaded, but no pages rendered. Please try another file."}), 400

                for img in images:
                    processed = preprocess(img)
                    extracted_text += pytesseract.image_to_string(Image.fromarray(processed))

            except Exception as pdf_err:
                return jsonify({"error": f"❌ PDF processing failed: {str(pdf_err)}"}), 500
            finally:
                os.remove(tmp_pdf_path)

        else:
            return jsonify({"error": "Unsupported file format."}), 400

        if not extracted_text.strip():
            return jsonify({"error": "❌ No text could be read. Try a clearer PDF or image scan."}), 400

        # AI summary
        prompt = (
            "You are a calm and caring AI assistant. A user has uploaded this medical scan/report text:\n\n"
            f"{extracted_text}\n\n"
            "Please explain it in simple, kind language. Gently summarize the key findings, and if it sounds alarming, add a calm disclaimer like: "
            "'Please don’t panic. This is only a machine reading and not a diagnosis. Always consult a doctor.'"
        )

        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)

        return jsonify({
            "extracted_text": extracted_text,
            "summary": response.text
        })

    except Exception as e:
        return jsonify({"error": f"Scan processing error: {str(e)}"}), 500



# --- Run Flask App ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
