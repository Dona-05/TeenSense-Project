from transformers import pipeline
import pandas as pd
from datetime import date
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
# LABEL MAPPING
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
# EMOTION DETECTION
# -------------------------------
def detect_emotion(text):
    return emotion_classifier(text)[0]

def get_primary(emotions):
    emotions = sorted(emotions, key=lambda x: x["score"], reverse=True)
    return emotions[0], emotions

def get_intensity(final_emotion):
    return "Low" if final_emotion == "Neutral" else "Medium"

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
# DAILY ANALYSIS
# -------------------------------
emotion_priority = {
    "Happy": 1,
    "Neutral": 2,
    "Sad": 3,
    "Anxious": 4,
    "Angry": 5
}

def daily_emotion_analysis(journal_answers):
    results = [process_journal(ans) for ans in journal_answers]
    results.sort(
        key=lambda x: emotion_priority.get(x["emotion"], 0),
        reverse=True
    )
    final_emotion = results[0]["emotion"]
    avg_confidence = round(
        sum(r["confidence"] for r in results) / len(results), 2
    )
    return {
        "final_emotion": final_emotion,
        "avg_confidence": avg_confidence,
        "all_results": results
    }
# -------------------------------
# SAVE DATA
# -------------------------------
def save_daily_emotion(emotion, confidence, source, journal_text=""):
    today = date.today().isoformat()
    data = {
        "date": today,
        "emotion": emotion,
        "confidence": confidence,
        "source": source,
        "journal_text": journal_text
    }
    file_name = "daily_emotions.csv"
    df = pd.DataFrame([data])
    if os.path.exists(file_name):
        df.to_csv(file_name, mode="a", header=False, index=False)
    else:
        df.to_csv(file_name, index=False)
# -------------------------------
# CHECK DAILY SUBMISSION
# -------------------------------
def already_submitted_today(source=None):
    try:
        df = pd.read_csv("daily_emotions.csv")
    except:
        return False
    today = date.today().isoformat()
    today_entries = df[df["date"] == today]
    # 🔹 if checking specific source (journal or emoji)
    if source:
        return any(today_entries["source"] == source)
    # 🔹 if checking ANY submission today
    return len(today_entries) > 0
# -------------------------------
# ALERT LOGIC
# -------------------------------
def check_for_supportive_guidance():
    try:
        df = pd.read_csv("daily_emotions.csv")
    except:
        return None
    if len(df) < 5:
        return None
    last_five = df.tail(5)["emotion"].tolist()
    negative_emotions = ["Sad", "Anxious", "Angry"]
    for i in range(len(last_five) - 2):
        window = last_five[i:i+3]
        if all(e in negative_emotions for e in window):
            dominant_emotion = max(set(window), key=window.count)
            guidance_templates = {
                "Sad": "Spend more time listening and offering reassurance.",
                "Anxious": "Provide calm reassurance and support.",
                "Angry": "Encourage open conversation to reduce frustration."
            }
            return {
                "alert": True,
                "emotion": dominant_emotion,
                "message": guidance_templates.get(
                    dominant_emotion,
                    "A supportive check-in may help."
                )
            }
    return None
