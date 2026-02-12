from transformers import pipeline
import pandas as pd

# -------------------------------
# LOAD FINE-TUNED EMOTION MODEL
# -------------------------------
emotion_classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    top_k=None,     # return all emotion scores
    device=-1       # CPU
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

def get_primary_and_dominance(emotions):
    emotions = sorted(emotions, key=lambda x: x["score"], reverse=True)
    top = emotions[0]
    second = emotions[1]
    dominance = round(top["score"] - second["score"], 2)
    return top, dominance, emotions

def get_intensity(dominance, final_emotion):
    if final_emotion == "Neutral":
        return "Low"
    if dominance < 0.2:
        return "Low"
    elif dominance < 0.5:
        return "Medium"
    else:
        return "High"

def get_top_k_emotions(emotions, k=3):
    top_k = emotions[:k]
    return [
        {
            "emotion": emotion_map.get(e["label"], "Neutral"),
            "score": round(e["score"], 2)
        }
        for e in top_k
    ]

def process_journal(text):
    emotions = detect_emotion(text)
    primary, dominance, sorted_emotions = get_primary_and_dominance(emotions)

    label = primary["label"]
    confidence = round(primary["score"], 2)
    final_emotion = emotion_map.get(label, "Neutral")

    intensity = get_intensity(dominance, final_emotion)
    ambiguous = dominance < 0.2
    top_emotions = get_top_k_emotions(sorted_emotions, k=3)

    return {
        "emotion": final_emotion,          # Primary emotion
        "confidence": confidence,          # Primary confidence
        "intensity": intensity,            # Low / Medium / High
        "dominance": dominance,            # Dominance score
        "ambiguous": ambiguous,            # Ambiguity flag
        "top_k_emotions": top_emotions     # Top-K emotions
    }

# -------------------------------
# DATASET SINGLE-ROW TEST
# -------------------------------
def test_excel_row(csv_path, excel_row_number):
    df = pd.read_csv(csv_path)

    row_index = excel_row_number - 2
    if row_index < 0 or row_index >= len(df):
        print("Invalid Excel row number")
        return

    text = df.iloc[row_index]["text"]
    prediction = process_journal(text)

    print("\nDATASET SINGLE ROW TEST\n")
    print(f"Excel Row Number: {excel_row_number}")
    print(f"Text: {text}")
    print("Prediction:")
    print(prediction)

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

    print("\n===== DATASET TEST (20th ROW) =====")
    test_excel_row(
        "C:/Users/dona jeny/Downloads/data/testdata.csv",
        excel_row_number=20
    )

    print("\n===== USER INPUT MODE =====")
    choice = input("Do you want to enter journal text? (y/n): ").lower()

    if choice == "y":
        user_inputs = get_user_journal_input()

        if user_inputs:
            result = daily_emotion_analysis(user_inputs)
            print("\nDAILY EMOTION SUMMARY")
            print(result)
    else:
        print("User input skipped.")