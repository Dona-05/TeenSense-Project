from transformers import pipeline
import pandas as pd

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
# MULTI-DAY EMOTION HISTORY
# -------------------------------
emotion_history = []   # stores daily summaries

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
        "top_k_emotions": get_top_k_emotions(sorted_emotions)
    }

# -------------------------------
# DAILY EMOTION ANALYSIS
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
# PHASE 3: MULTI-DAY TREND ANALYSIS
# -------------------------------
def detect_multi_day_trend(history, window=3):
    if len(history) < window:
        return "Not enough data for trend analysis"

    recent_days = history[-window:]
    emotions = [day["emotion"] for day in recent_days]

    if all(e == emotions[0] for e in emotions):
        return f"Persistent {emotions[0]} emotion trend"

    return "No persistent emotional trend"

def generate_emotion_alert(trend_result):
    if any(e in trend_result for e in ["Sad", "Anxious", "Angry"]):
        return "⚠ Alert: Prolonged negative emotional state detected"
    return "No alert generated"

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

    print("\n===== USER INPUT MODE =====")
    choice = input("Do you want to enter journal text? (y/n): ").lower()

    if choice == "y":
        user_inputs = get_user_journal_input()

        if user_inputs:
            result = daily_emotion_analysis(user_inputs)

            # Store daily summary
            emotion_history.append({
                "emotion": result["final_emotion"],
                "confidence": result["avg_confidence"]
            })

            # Trend + alert
            trend = detect_multi_day_trend(emotion_history)
            alert = generate_emotion_alert(trend)

            print("\nDAILY EMOTION SUMMARY")
            print(result)

            print("\nTREND ANALYSIS:", trend)
            print("ALERT STATUS:", alert)

    else:
        print("User input skipped.")
