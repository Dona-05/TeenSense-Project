import pandas as pd

# -------------------------------
# CONFIGURATION
# -------------------------------
NEGATIVE_EMOTIONS = ["Sad", "Anxious", "Angry"]
WINDOW_SIZE = 5               # last 5 days only
ALERT_THRESHOLD_DAYS = 4      # 4 out of 5 negative days → alert

# -------------------------------
# MULTI-DAY SLIDING WINDOW ANALYSIS
# -------------------------------
def analyze_multi_day_trend(csv_path="daily_emotions.csv"):
    df = pd.read_csv(csv_path)

    if df.empty:
        print("No data available for analysis.")
        return

    # Take only the most recent WINDOW_SIZE days
    recent_df = df.tail(WINDOW_SIZE)

    total_days = len(recent_df)
    negative_days = recent_df["emotion"].isin(NEGATIVE_EMOTIONS).sum()

    print("\n===== MULTI-DAY EMOTION TREND ANALYSIS =====")
    print(f"Days Considered (Window) : Last {total_days} days")
    print(f"Negative Emotion Days    : {negative_days}")

    if negative_days >= ALERT_THRESHOLD_DAYS:
        print("\nTREND DETECTED : Persistent negative emotional state")
        print("ALERT STATUS  : ⚠ Mental health risk detected")
    else:
        print("\nTREND STATUS  : Emotional state within normal range")
        print("ALERT STATUS : No alert")

# -------------------------------
# MAIN EXECUTION
# -------------------------------
if __name__ == "__main__":
    analyze_multi_day_trend()
