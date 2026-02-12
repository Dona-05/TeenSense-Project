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

if __name__ == "__main__":
    test_texts = [
        "I feel very sad and lonely today",
        "I am extremely happy with my results",
        "I feel anxious and stressed about exams",
        "Nothing special happened today"
    ]

    for text in test_texts:
        print("\nJournal Text:", text)
        emotions = detect_emotion(text)
        for e in emotions:
            print(f"{e['label']} -> {round(e['score'], 2)}")
