import matplotlib
matplotlib.use('Agg')
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
import matplotlib.pyplot as plt

app = Flask(__name__)

# Initialize database
DB_FILE = "patients.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS patients
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS symptoms
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  patient_id INTEGER,
                  blurred_vision INTEGER,
                  eye_discomfort INTEGER,
                  light_sensitivity INTEGER,
                  fatigue INTEGER,
                  risk_score REAL,
                  date TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Risk calculation
def calculate_risk(blurred_vision, eye_discomfort, light_sensitivity, fatigue):
    score = (blurred_vision / 5 * 0.4 +
             eye_discomfort / 5 * 0.3 +
             light_sensitivity / 5 * 0.2 +
             fatigue / 5 * 0.1) * 100
    return round(score, 2)

# Routes
@app.route("/")
def index():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM patients")
    patients = c.fetchall()
    conn.close()
    return render_template("index.html", patients=patients)

@app.route("/add_patient", methods=["POST"])
def add_patient():
    name = request.form["name"]
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO patients (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/log_symptom/<int:patient_id>", methods=["GET", "POST"])
def log_symptom(patient_id):
    if request.method == "POST":
        blurred_vision = int(request.form["blurred_vision"])
        eye_discomfort = int(request.form["eye_discomfort"])
        light_sensitivity = int(request.form["light_sensitivity"])
        fatigue = int(request.form["fatigue"])
        risk_score = calculate_risk(blurred_vision, eye_discomfort, light_sensitivity, fatigue)
        date = request.form["date"]

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""INSERT INTO symptoms
                     (patient_id, blurred_vision, eye_discomfort, light_sensitivity, fatigue, risk_score, date)
                     VALUES (?, ?, ?, ?, ?, ?, ?)""",
                  (patient_id, blurred_vision, eye_discomfort, light_sensitivity, fatigue, risk_score, date))
        conn.commit()
        conn.close()
        return redirect(url_for("dashboard"))
    else:
        return render_template("log_symptom.html", patient_id=patient_id)

@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""SELECT s.id, p.name, s.risk_score, s.date
                 FROM symptoms s JOIN patients p ON s.patient_id = p.id
                 ORDER BY s.date DESC""")
    data = c.fetchall()
    conn.close()

    # Generate chart
    if data:
        dates = [row[3] for row in data]
        scores = [row[2] for row in data]
        plt.figure(figsize=(5,3))
        plt.plot(dates, scores, marker='o')
        plt.title("Risk Scores Over Time")
        plt.xlabel("Date")
        plt.ylabel("Risk Score")
        plt.tight_layout()
        chart_path = "static/risk_chart.png"
        plt.savefig(chart_path)
        plt.close()
    else:
        chart_path = None

    return render_template("dashboard.html", data=data, chart_path=chart_path)

if __name__ == "__main__":
    app.run(debug=True)

