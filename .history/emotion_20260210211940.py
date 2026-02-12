from transformers import pipeline
import pandas as pd
from datetime import datetime
import os

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
# EMOTION PRIORITY (FOR DAILY FINAL)
# -------------------------------
emotion_priority = {
    "Happy": 1,
    "Neutral": 2,
    "Sad": 3,
    "Anxious": 4,
    "Angry": 5
}

# -------------------------------
# EMOTION FUNCTIONS
# -------------------------------
def detect_emotion(text):
    return emotion_classifier(text)[0]

def get_primary(emotions):
    emotions = sorted(emotions, key=lambda x: x["score"], reverse=True)
    return emotions[0], emotions

def get_intensity(final_emotion):
    if final_emotion == "Neutral":
        return "Low"
    else:
        return "Medium"

def get_top_k_emotions(emotions, k=3):
    return [
        {
            "emotion": emotion_map.get(e["label"], "Neutral"),
            "score": round(e["score"], 2)
        }
        for e in emotions[:k]
    ]

def process_journal(text):
    emotions = detect_emotion(text)
    primary, sorted_emotions = get_primary(emotions)

    final_emotion = emotion_map.get(primary["label"], "Neutral")

    return {
        "emotion": final_emotion,
        "confidence": round(primary["score"], 2),
        "intensity": get_intensity(final_emotion),
        "ambiguous": False,
        "top_k_emotions": get_top_k_emotions(sorted_emotions)
    }

# -------------------------------
# DAILY EMOTION ANALYSIS
# -------------------------------
def daily_emotion_analysis(journal_entries):
    results = [process_journal(text) for text in journal_entries]

    # Pick dominant emotion using priority
    results.sort(
        key=lambda x: emotion_priority.get(x["emotion"], 0),
        reverse=True
    )

    final_emotion = results[0]["emotion"]
    avg_confidence = round(
        sum(r["confidence"] for r in results) / len(results), 2
    )

    return final_emotion, avg_confidence, results

# -------------------------------
# SAVE DAILY RESULT TO CSV
# -------------------------------
def save_daily_result(emotion, confidence):
    today = datetime.now().strftime("%Y-%m-%d")
    file_path = "daily_emotions.csv"

    new_row = {
        "date": today,
        "emotion": emotion,
        "confidence": confidence
    }

    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    else:
        df = pd.DataFrame([new_row])

    df.to_csv(file_path, index=False)

# -------------------------------
# USER INPUT MODE
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

    user_inputs = get_user_journal_input()

    if user_inputs:
        final_emotion, avg_confidence, all_results = daily_emotion_analysis(user_inputs)

        print("\nDAILY EMOTION SUMMARY")
        print("Final Emotion :", final_emotion)
        print("Avg Confidence:", avg_confidence)
        print("All Results  :", all_results)

        save_daily_result(final_emotion, avg_confidence)
        print("\nDaily emotion saved successfully.")
    else:
        print("No input provided.")
