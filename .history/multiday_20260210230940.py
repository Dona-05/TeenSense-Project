import pandas as pd

# -------------------------------
# CONFIGURATION
# -------------------------------
NEGATIVE_EMOTIONS = ["Sad", "Anxious", "Angry"]
WINDOW_SIZE = 5               # last 5 days only
ALERT_THRESHOLD_DAYS = 4      # 4 out of 5 days

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
    print(f"High-Stress Emotion Days : {negative_days}")

    # -------------------------------
    # ALERT LOGIC (NON-DIAGNOSTIC)
    # -------------------------------
    if negative_days >= ALERT_THRESHOLD_DAYS:
        print("\nTREND STATUS : Sustained emotional stress pattern observed")
        print("SUPPORT MESSAGE :")
        print(
            "Recent emotional patterns suggest increased stress.\n"
            "A gentle check-in and supportive conversation are recommended.\n"
            "This system does not diagnose mental health conditions."
        )
    else:
        print("\nTREND STATUS : Emotional state appears stable")
        print("SUPPORT MESSAGE : No immediate action required")

# -------------------------------
# MAIN EXECUTION
# -------------------------------
if __name__ == "__main__":
    analyze_multi_day_trend()
