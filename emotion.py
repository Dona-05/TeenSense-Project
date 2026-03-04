from transformers import pipeline
import pandas as pd
from datetime import date

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
# SAVE DAILY EMOTION
# -------------------------------
def save_daily_emotion(emotion, confidence, source):
    today = date.today().isoformat()

    data = {
        "date": today,
        "emotion": emotion,
        "confidence": confidence,
        "source": source
    }

    df = pd.DataFrame([data])

    try:
        df.to_csv("daily_emotions.csv", mode="a", header=False, index=False)
    except FileNotFoundError:
        df.to_csv("daily_emotions.csv", index=False)

    print("Daily mood recorded successfully.")

# -------------------------------
# CHECK LAST 5 ENTRIES
# LOOK FOR 3 CONSECUTIVE NEGATIVES
# -------------------------------
def check_for_supportive_guidance():
    try:
        df = pd.read_csv("daily_emotions.csv")
    except FileNotFoundError:
        return

    # Require at least 5 total entries
    if len(df) < 5:
        return

    last_five = df.tail(5)["emotion"].tolist()
    negative_emotions = ["Sad", "Anxious", "Angry"]

    # Slide window of 3 inside last 5
    for i in range(len(last_five) - 2):
        window = last_five[i:i+3]

        if all(emotion in negative_emotions for emotion in window):

            dominant_emotion = max(set(window), key=window.count)

            if dominant_emotion in ["Angry", "Anxious"]:
                intensity = "Moderate"
            else:
                intensity = "Mild"

            guidance_templates = {
                "Sad": "It may be helpful to spend a little extra time listening and offering reassurance.",
                "Anxious": "A calm conversation and reassurance about support and safety may be beneficial.",
                "Angry": "Encouraging open discussion about what might be causing frustration could help."
            }

            print("\n==============================")
            print("        GENTLE ALERT")
            print("==============================")
            print(f"Dominant Emotion : {dominant_emotion}")
            print(f"Intensity        : {intensity}")
            print()
            print(guidance_templates.get(
                dominant_emotion,
                "A supportive check-in may be helpful at this time."
            ))
            print("==============================\n")

            break  # Stop after first pattern found

# -------------------------------
# JOURNAL INPUT MODE
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
# DAILY MOOD CHECK-IN (EMOJI)
# -------------------------------
def mood_check_in():
    print("\n===== DAILY MOOD CHECK-IN =====")
    print("Choose how you feel today:\n")

    print("1. 😊 Happy")
    print("2. 😢 Sad")
    print("3. 😰 Anxious")
    print("4. 😠 Angry")
    print("5. 😐 Neutral")

    choice = input("Enter choice (1-5): ").strip()

    emoji_map = {
        "1": "Happy",
        "2": "Sad",
        "3": "Anxious",
        "4": "Angry",
        "5": "Neutral"
    }

    if choice in emoji_map:
        emotion_selected = emoji_map[choice]

        save_daily_emotion(
            emotion_selected,
            1.0,
            "emoji"
        )

        check_for_supportive_guidance()

    else:
        print("Invalid selection.")

# -------------------------------
# MAIN EXECUTION
# -------------------------------
if __name__ == "__main__":

    print("\n===== TEENSENSE DAILY CHECK =====")
    print("1. Write Journal Entry")
    print("2. Daily Mood Check-In (Quick)")

    option = input("Choose an option (1/2): ").strip()

    if option == "1":
        user_inputs = get_user_journal_input()

        if user_inputs:
            result = daily_emotion_analysis(user_inputs)

            print("\nDAILY EMOTION SUMMARY")
            print(result)

            save_daily_emotion(
                result["final_emotion"],
                result["avg_confidence"],
                "journal"
            )

            check_for_supportive_guidance()

    elif option == "2":
        mood_check_in()

    else:
        print("Invalid option selected.")