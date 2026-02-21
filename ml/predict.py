import pandas as pd
import joblib
import os
import numpy as np

# =========================
# BASE DIRECTORY
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# =========================
# LOAD TRAINED MODEL
# =========================
model = joblib.load(os.path.join(BASE_DIR, "model.pkl"))

# =========================
# LOAD SYMPTOMS LIST
# =========================
with open(os.path.join(BASE_DIR, "..", "symptoms.txt")) as f:
    symptoms = [line.strip() for line in f if line.strip()]

# =========================
# LOAD AI INPUT FILE
# =========================
input_path = os.path.join(BASE_DIR, "..", "ai_input.csv")
input_data = pd.read_csv(input_path)

# Remove junk columns
input_data = input_data.loc[:, ~input_data.columns.str.contains("^unnamed", case=False)]

# Ensure correct feature order
input_data = input_data.reindex(columns=symptoms, fill_value=0)

# =========================
# PREDICT CATEGORY
# =========================
probs = model.predict_proba(input_data)[0]
classes = model.classes_

# Get highest probability prediction
top_idx = np.argmax(probs)
predicted_category = classes[top_idx]
confidence = probs[top_idx] * 100

# =========================
# CATEGORY → DOCTOR MAP
# =========================
specialist_map = {
    "Heart": "Cardiologist",
    "Brain": "Neurologist",
    "Respiratory": "Pulmonologist",
    "Liver": "Hepatologist",
    "Endocrine": "Endocrinologist",
    "Mental_Health": "Psychiatrist",
    "Skin": "Dermatologist",
    "General": "General Physician"
}

doctor = specialist_map.get(predicted_category, "General Physician")

# =========================
# OUTPUT RESULT
# =========================
print("AI MEDICAL ASSISTANT RESULT")
print("----------------------------")
print(f"Category Identified   : {predicted_category}")
print(f"Confidence            : {confidence:.2f}%")
print(f"Recommended Doctor    : {doctor}")
print("----------------------------")
