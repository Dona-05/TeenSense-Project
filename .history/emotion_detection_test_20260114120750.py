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
        "My day was productive and largely positive. It began with the usual morning rush, but I managed to catch the bus with a few minutes to spare, which always sets a good tone. At school, I had an engaging English class where we started an interesting new project, followed by lunch with friends where we shared a lot of laughs. After classes ended, I spent a couple of hours at the library finishing up some challenging homework. I arrived home in the evening, enjoyed a home-cooked meal with my family, and spent some time relaxing before preparing my things for tomorrow. As the day comes to an end, I feel a sense of accomplishment and gratitude for the little moments that made it special."
    ]

    for text in test_texts:
        print("\nJournal Text:", text)
        emotions = detect_emotion(text)
        for e in emotions:
            print(f"{e['label']} -> {round(e['score'], 2)}")
