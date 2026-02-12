from transformers import pipeline
import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix

# -------------------------------
# LOAD EMOTION MODEL
# -------------------------------
emotion_classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    top_k=None,
    device=-1
)

# -------------------------------
# MODEL LABEL → PROJECT LABEL
# -------------------------------
emotion_map = {
    "sadness": "Sad",
    "fear": "Anxious",
    "anger": "Angry",
    "joy": "Happy",
    "love": "Happy",
    "surprise": "Anxious",
    "neutral": "Neutral"
}

# -------------------------------
# DATASET LABEL → PROJECT LABEL
# -------------------------------
dataset_label_map = {
    "joy": "Happy",
    "love": "Happy",
    "admiration": "Happy",
    "amusement": "Happy",
    "approval": "Happy",

    "sadness": "Sad",
    "disappointment": "Sad",
    "grief": "Sad",

    "anger": "Angry",
    "annoyance": "Angry",
    "disgust": "Angry",

    "fear": "Anxious",
    "nervousness": "Anxious",

    "neutral": "Neutral",
    "confusion": "Neutral",
    "curiosity": "Neutral",
    "realization": "Neutral"
}

# -------------------------------
# EMOTION DETECTION (SINGLE OUTPUT)
# -------------------------------
def detect_emotion(text):
    emotions = emotion_classifier(text)[0]
    primary = max(emotions, key=lambda x: x["score"])
    return emotion_map.get(primary["label"], "Neutral")

# -------------------------------
# PERFORMANCE EVALUATION
# -------------------------------
def evaluate_model(csv_path):
    df = pd.read_csv(csv_path)

    y_true = []
    y_pred = []

    for _, row in df.iterrows():
        y_pred.append(detect_emotion(row["text"]))
        y_true.append(dataset_label_map.get(row["label"].lower(), "Neutral"))

    accuracy = accuracy_score(y_true, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="weighted", zero_division=0
    )

    cm = confusion_matrix(y_true, y_pred)

    return {
        "accuracy": accuracy * 100,
        "precision": precision * 100,
        "recall": recall * 100,
        "f1_score": f1 * 100,
        "confusion_matrix": cm
    }

# -------------------------------
# USER INPUT MODE
# -------------------------------
def user_input_mode():
    print("\n===== USER JOURNAL INPUT MODE =====")
    print("Type your journal text (type 'done' to finish)\n")

    while True:
        text = input("➤ ")
        if text.lower() == "done":
            break
        if not text.strip():
            continue

        final_emotion = detect_emotion(text)
        print(f"Final Emotion: {final_emotion}")
        print("-" * 30)

# -------------------------------
# MAIN EXECUTION
# -------------------------------
if __name__ == "__main__":

    print("\n===== MODEL PERFORMANCE EVALUATION =====")

    metrics = evaluate_model(
        "C:/Users/dona jeny/Downloads/data/emotion_test.csv"
    )

    print(f"Accuracy   : {metrics['accuracy']:.2f}%")
    print(f"Precision  : {metrics['precision']:.2f}%")
    print(f"Recall     : {metrics['recall']:.2f}%")
    print(f"F1-score   : {metrics['f1_score']:.2f}%")
    print("Confusion Matrix:\n", metrics["confusion_matrix"])

    choice = input("\nDo you want to enter journal text? (y/n): ").lower()
    if choice == "y":
        user_input_mode()
    else:
        print("User input skipped.")
