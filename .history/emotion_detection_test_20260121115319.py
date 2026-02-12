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
# EMOTION FUNCTIONS (NO CONFIDENCE)
# -------------------------------
def detect_emotion(text):
    return emotion_classifier(text)[0]

def get_primary_emotion(emotions):
    emotions = sorted(emotions, key=lambda x: x["score"], reverse=True)
    return emotions[0], emotions

def get_top_k_emotions(emotions, k=3):
    return [
        emotion_map.get(e["label"], "Neutral")
        for e in emotions[:k]
    ]

def process_journal(text):
    emotions = detect_emotion(text)
    primary, sorted_emotions = get_primary_emotion(emotions)

    final_emotion = emotion_map.get(primary["label"], "Neutral")

    return {
        "emotion": final_emotion,
        "top_k_emotions": get_top_k_emotions(sorted_emotions, k=3)
    }

# -------------------------------
# PERFORMANCE EVALUATION
# -------------------------------
def evaluate_model(csv_path):
    """
    CSV must contain:
    - text
    - label (true emotion)
    """
    df = pd.read_csv("C:/Users/dona jeny/Downloads/data/emotion_test.csv")

    y_true = []
    y_pred = []

    for _, row in df.iterrows():
        prediction = process_journal(row["text"])
        y_pred.append(prediction["emotion"])
        y_true.append(row["label"])

    accuracy = accuracy_score(y_true, y_pred)

    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="weighted"
    )

    cm = confusion_matrix(y_true, y_pred)

    return {
        "accuracy": round(accuracy, 3),
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1_score": round(f1, 3),
        "confusion_matrix": cm
    }

# -------------------------------
# USER INPUT MODE (INFERENCE ONLY)
# -------------------------------
def get_user_journal_input():
    print("\nEnter today's journal entries (type 'done' to finish):")
    entries = []

    while True:
        text = input("➤ ")
        if text.lower() == "done":
            break
        if text.strip():
            entries.append(text)

    return entries

# -------------------------------
# MAIN EXECUTION
# -------------------------------
if __name__ == "__main__":

    print("\n===== MODEL PERFORMANCE EVALUATION =====")
    metrics = evaluate_model(
        "C:/Users/dona jeny/Downloads/data/emotion_test.csv"
    )

    print("Accuracy:", metrics["accuracy"])
    print("Precision:", metrics["precision"])
    print("Recall:", metrics["recall"])
    print("F1-score:", metrics["f1_score"])
    print("Confusion Matrix:\n", metrics["confusion_matrix"])

    print("\n===== USER INPUT MODE =====")
    choice = input("Do you want to enter journal text? (y/n): ").lower()

    if choice == "y":
        user_inputs = get_user_journal_input()

        for text in user_inputs:
            print(process_journal(text))
    else:
        print("User input skipped.")
