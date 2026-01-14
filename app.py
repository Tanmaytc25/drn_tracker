# Built-ins imports to fix Pylance warnings # CI/CD test comment
from builtins import round, int, list, reversed

import os
import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, redirect, url_for
from analysis.process_simulation import process_simulation
from datetime import datetime

# ----------------------------
# Initialize Flask
# ----------------------------
app = Flask(__name__)

# ----------------------------
# Database config
# ----------------------------
DB_FILE = "patients.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Patients table
    c.execute('''CREATE TABLE IF NOT EXISTS patients
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT)''')
    # Symptoms table
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

# ----------------------------
# Risk calculation
# ----------------------------
def calculate_risk(blurred_vision, eye_discomfort, light_sensitivity, fatigue):
    score = (blurred_vision / 5 * 0.4 +
             eye_discomfort / 5 * 0.3 +
             light_sensitivity / 5 * 0.2 +
             fatigue / 5 * 0.1) * 100
    return round(score, 2)

# ----------------------------
# Routes
# ----------------------------

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
        date = request.form.get("date") or datetime.today().strftime("%Y-%m-%d")

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

    # Convert to dicts for template
    results = [{"id": row[0], "name": row[1], "risk_score": row[2], "date": row[3]} for row in data]

    # Generate overall chart
    chart_path = None
    if results:
        chart_path = "static/risk_chart.png"
        dates = [r['date'] for r in results]
        scores = [r['risk_score'] for r in results]
        plt.figure(figsize=(6,4))
        plt.plot(dates, scores, marker='o', color='blue')
        plt.title("Risk Scores Over Time")
        plt.xlabel("Date")
        plt.ylabel("Risk Score")
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        os.makedirs("static", exist_ok=True)
        plt.savefig(chart_path)
        plt.close()

    return render_template("dashboard.html", data=results, chart_path=chart_path)

@app.route('/run_simulation/<patient_name>')
def run_simulation(patient_name):
    csv_file = 'data_samples/sample_patient.csv'  # simulated input
    results = process_simulation(patient_name, csv_file)

    # Ensure results folder exists
    results_dir = os.path.join("static", "results")
    os.makedirs(results_dir, exist_ok=True)

    # Generate patient-specific chart
    chart_path = os.path.join(results_dir, f"{patient_name}_risk_chart.png")
    dates = [r['date'] for r in results]
    scores = [r['risk_score'] for r in results]
    plt.figure(figsize=(6,4))
    plt.plot(dates, scores, marker='o', color='green')
    plt.title(f"Risk Scores Over Time - {patient_name}")
    plt.xlabel("Date")
    plt.ylabel("Risk Score")
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

    return render_template("dashboard.html", data=results, chart_path=chart_path)

# ----------------------------
# Run Flask
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)




