from transformers import pipeline

# Load emotion detection pipeline
emotion_classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    top_k=None,          # replaces return_all_scores (new standard)
    device=-1            # force CPU
)

def detect_emotion(text):
    return emotion_classifier(text)[0]
def get_primary_emotion(emotions):
    """
    Selects emotion with highest confidence
    """
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

if __name__ == "__main__":
    texts = [
        "I feel very sad and lonely today",
        "I am extremely happy with my results",
        "I feel anxious and stressed about exams",
        "Nothing special happened today"
    ]

    for t in texts:
        result = process_journal(t)
        print("\nJournal:", t)
        print(result)

from transformers import pipeline

# Load emotion detection pipeline
emotion_classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    top_k=None,          # replaces return_all_scores (new standard)
    device=-1            # force CPU
)



emotion_map = {
    "sadness": "Sad",
    "fear": "Anxious",
    "anger": "Angry",
    "joy": "Happy",
    "neutral": "Neutral"
}

