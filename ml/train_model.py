import pandas as pd
import os
import joblib
from sklearn.ensemble import RandomForestClassifier

# =========================
# BASE DIRECTORY
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# =========================
# LOAD DATA
# =========================
data_path = os.path.join(BASE_DIR, "..", "Dataset", "Training.csv")
df = pd.read_csv(data_path)

print("✅ Training data loaded")
print("📐 Shape:", df.shape)

# =========================
# CLEAN COLUMN NAMES
# =========================
df.columns = (
    df.columns.str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace("__+", "_", regex=True)
    .str.replace(".", "", regex=False)
)

# Remove unnamed + duplicate columns
df = df.loc[:, ~df.columns.str.contains("^unnamed")]
df = df.loc[:, ~df.columns.str.contains(r"\d+$", regex=True)]

# =========================
# LOAD DISEASE → CATEGORY MAP
# =========================
map_path = os.path.join(BASE_DIR, "disease_category_map.csv")
map_df = pd.read_csv(map_path)

disease_to_category = dict(
    zip(map_df["disease"].str.strip().str.lower(),
        map_df["category"].str.strip())
)

# =========================
# MAP PROGNOSIS → CATEGORY
# =========================
df["category"] = df["prognosis"].str.strip().str.lower().map(disease_to_category)
df["category"] = df["category"].fillna("General")

# =========================
# SEPARATE GENERAL / NON-GENERAL
# =========================
general_df = df[df["category"] == "General"]
non_general_df = df[df["category"] != "General"]

# =========================
# BALANCE NON-GENERAL CLASSES
# =========================
min_class_size = non_general_df["category"].value_counts().min()

balanced_non_general = (
    non_general_df
    .groupby("category", group_keys=False)
    .apply(lambda x: x.sample(min_class_size, random_state=42))
)

# =========================
# LIMIT GENERAL CLASS (IMPORTANT)
# =========================
general_sample_size = min_class_size  # same as one category
general_balanced = general_df.sample(
    n=min(len(general_df), general_sample_size),
    random_state=42
)

# =========================
# FINAL TRAINING DATA
# =========================
final_df = pd.concat([balanced_non_general, general_balanced])
final_df = final_df.sample(frac=1, random_state=42).reset_index(drop=True)

print("\n📊 Category Distribution (After De-biasing):")
print(final_df["category"].value_counts())

# =========================
# SPLIT FEATURES / LABEL
# =========================
X = final_df.drop(["prognosis", "category"], axis=1)
y = final_df["category"]

print("🧾 Feature count:", X.shape[1])

# =========================
# SAVE SYMPTOMS LIST
# =========================
symptoms_path = os.path.join(BASE_DIR, "..", "symptoms.txt")
with open(symptoms_path, "w") as f:
    for col in X.columns:
        f.write(col + "\n")

print("🧾 symptoms.txt regenerated")

# =========================
# TRAIN MODEL
# =========================
model = RandomForestClassifier(
    n_estimators=300,
    max_depth=18,
    min_samples_leaf=3,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)

model.fit(X, y)

# =========================
# SAVE MODEL
# =========================
model_path = os.path.join(BASE_DIR, "model.pkl")
joblib.dump(model, model_path)

print("\n✅ MODEL TRAINING COMPLETE")
print("📦 Model saved as ml/model.pkl")
