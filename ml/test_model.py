import pandas as pd
import joblib
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import os

# =========================
# BASE DIRECTORY
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# =========================
# LOAD MODEL
# =========================
model_path = os.path.join(BASE_DIR, "model.pkl")
model = joblib.load(model_path)

# =========================
# LOAD TEST DATA
# =========================
test_path = os.path.join(BASE_DIR, "..", "Dataset", "Testing.csv")
test_data = pd.read_csv(test_path)

# =========================
# COLUMN CLEANING (MATCH TRAINING)
# =========================
test_data.columns = (
    test_data.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace("__+", "_", regex=True)
    .str.replace(".", "", regex=False)
)

# =========================
# REMOVE GARBAGE COLUMNS
# =========================
test_data = test_data.loc[
    :, ~test_data.columns.str.contains("^unnamed", case=False)
]

test_data = test_data.loc[
    :, ~test_data.columns.str.contains(r"\d+$", regex=True)
]

# =========================
# SPLIT FEATURES & LABEL
# =========================
X_test = test_data.drop("prognosis", axis=1)
y_test = test_data["prognosis"]

# =========================
# DISEASE → CATEGORY MAP
# =========================
map_path = os.path.join(BASE_DIR, "disease_category_map.csv")
map_df = pd.read_csv(map_path)

disease_map = dict(zip(map_df["disease"], map_df["category"]))

y_test_category = y_test.map(disease_map)
y_test_category.fillna("General", inplace=True)

# =========================
# ALIGN FEATURES
# =========================
X_test = X_test.reindex(columns=model.feature_names_in_, fill_value=0)

# =========================
# PREDICTION
# =========================
y_pred = model.predict(X_test)

# =========================
# METRICS
# =========================
accuracy = accuracy_score(y_test_category, y_pred)

print("\n🎯 MODEL EVALUATION RESULT")
print("--------------------------------")
print(f"📊 Category Prediction Accuracy: {accuracy * 100:.2f}%")
print("--------------------------------")

print("\n📋 CLASSIFICATION REPORT")
print("--------------------------------")
print(classification_report(y_test_category, y_pred))

print("\n📊 CONFUSION MATRIX")
print("--------------------------------")
print(confusion_matrix(y_test_category, y_pred))
