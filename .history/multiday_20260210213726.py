import pandas as pd

# -------------------------------
# CONFIGURATION
# -------------------------------
NEGATIVE_EMOTIONS = ["Sad", "Anxious", "Angry"]
ALERT_THRESHOLD_DAYS = 4   # trigger alert if >=4 negative days

# -------------------------------
# MULTI-DAY TREND ANALYSIS
# -------------------------------
def analyze_multi_day_trend(csv_path="daily_emotions.csv"):
    df = pd.read_csv(csv_path)

    if df.empty:
        print("No data available for analysis.")
        return

    total_days = len(df)
    negative_days = df["emotion"].isin(NEGATIVE_EMOTIONS).sum()

    print("\n===== MULTI-DAY EMOTION TREND ANALYSIS =====")
    print(f"Total Days Analysed   : {total_days}")
    print(f"Negative Emotion Days : {negative_days}")

    if negative_days >= ALERT_THRESHOLD_DAYS:
        print("\nTREND DETECTED : Persistent negative emotional pattern")
        print("ALERT STATUS  : ⚠ Mental health risk detected")
    else:
        print("\nTREND STATUS  : Emotional state within normal range")
        print("ALERT STATUS : No alert")

# -------------------------------
# MAIN EXECUTION
# -------------------------------
if __name__ == "__main__":
    analyze_multi_day_trend()
