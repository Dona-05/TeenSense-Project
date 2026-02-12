from transformers import pipeline
import pandas as pd

# -------------------------------
# LOAD FINE-TUNED EMOTION MODEL
# -------------------------------
emotion_classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    top_k=None,
    device=-1   # CPU
)

# -------------------------------
# MODEL LABEL → PROJECT LABEL
# dair-ai/emotion labels
# -------------------------------
emotion_map = {
    "sadness": "Sad",
    "fear": "Anxious",
    "anger": "Angry",
    "joy": "Happy",
    "love": "Happy",
    "surprise": "Anxious"
}

# -------------------------------
# EMOTION FUNCTIONS
# -------------------------------
def detect_emotion(text):
    return emotion_classifier(text)[0]

def get_primary_emotion(emotions):
    return max(emotions, key=lambda x: x["score"])

def get_intensity(score):
    if score < 0.4:
        return "Low"
    elif score < 0.7:
        return "Medium"
    else:
        return "High"

def process_journal(text):
    emotions = detect_emotion(text)
    primary = get_primary_emotion(emotions)

    final_emotion = emotion_map[primary["label"]]
    confidence = round(primary["score"], 2)
    intensity = get_intensity(confidence)

    return {
        "emotion": final_emotion,
        "confidence": confidence,
        "intensity": intensity
    }

# -------------------------------
# DATASET SINGLE-ROW TEST
# -------------------------------
def test_excel_row(csv_path, excel_row_number):
    df = pd.read_csv(csv_path)

    # Excel row number → pandas index
    row_index = excel_row_number - 2

    if row_index < 0 or row_index >= len(df):
        print("Invalid Excel row number")
        return

    text = df.iloc[row_index]["text"]
    prediction = process_journal(text)

    print("\nDATASET SINGLE ROW TEST\n")
    print(f"Excel Row Number: {excel_row_number}")
    print(f"Text: {text}")
    print(f"Predicted Emotion: {prediction['emotion']}")
    print(f"Confidence: {prediction['confidence']}")
    print(f"Intensity: {prediction['intensity']}")

# -------------------------------
# DAILY EMOTION ANALYSIS
# -------------------------------
emotion_priority = {
    "Happy": 1,
    "Sad": 2,
    "Anxious": 3,
    "Angry": 4
}

def daily_emotion_analysis(journal_answers):
    results = [process_journal(ans) for ans in journal_answers]

    results.sort(
        key=lambda x: emotion_priority[x["emotion"]],
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

    print("\n===== DATASET TEST (83rd ROW) =====")
    test_excel_row(
        "C:/Users/dona jeny/Downloads/data/testdata.csv",
        excel_row_number=83
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
