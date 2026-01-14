# Built-ins imports to fix Pylance warnings
from builtins import range, round, list, reversed

import csv
from datetime import datetime, timedelta
import random

def process_simulation(patient_name, csv_file):
    """
    Simulates patient risk scores over 7 days.
    Returns a list of dicts: [{'patient_name': ..., 'date': ..., 'risk_score': ...}, ...]
    """
    results = []

    # Simulate 7 days of risk data
    base_date = datetime.today()
    for i in range(7):
        risk_score = round(random.uniform(10, 90), 2)
        date_str = (base_date - timedelta(days=i)).strftime("%Y-%m-%d")
        results.append({"patient_name": patient_name,
                        "date": date_str,
                        "risk_score": risk_score})

    return list(reversed(results))  # chronological order




