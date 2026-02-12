from transformers import pipeline

# Load emotion detection pipeline
emotion_classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    top_k=None,
    device=-1
)

# Map model labels to project labels
emotion_map = {
    "sadness": "Sad",
    "fear": "Anxious",
    "anger": "Angry",
    "joy": "Happy",
    "neutral": "Neutral"
}

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

def daily_emotion_analysis(journal_answers):
    results = []

    for ans in journal_answers:
        res = process_journal(ans)
        results.append(res)

    # sort by risk priority
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
if __name__ == "__main__":
    daily_answers = [
        "I feel stressed about my exams",
        "I was sad during class today",
        "I am worried about my future"
    ]

    result = daily_emotion_analysis(daily_answers)
    print("\nDAILY EMOTION SUMMARY")
    print(result)

