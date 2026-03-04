import csv
from datetime import datetime, timedelta
import os

FILE_NAME = "reminders.csv"

# Create file if not exists
def initialize_reminder_file():
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["event", "date", "role", "last_notified"])


# Add Reminder
def add_reminder():
    initialize_reminder_file()

    event = input("Enter event name: ")
    date = input("Enter event date (YYYY-MM-DD): ")
    role = input("Who is this for? (teen/parent/both): ")

    with open(FILE_NAME, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([event, date, role, ""])

    print("Reminder added successfully.\n")


# Check Upcoming Reminders (3 days before + event day)
def check_upcoming_reminders():
    initialize_reminder_file()

    today = datetime.today().date()
    updated_rows = []

    with open(FILE_NAME, mode='r') as file:
        reader = csv.DictReader(file)

        for row in reader:
            event_date = datetime.strptime(row["date"], "%Y-%m-%d").date()
            last_notified = row["last_notified"]

            days_left = (event_date - today).days

            # Show reminder if within 3 days and not already notified today
            if 0 <= days_left <= 3 and last_notified != str(today):

                if days_left == 0:
                    print(f"\n🔔 REMINDER: {row['event']} is TODAY!\n")
                else:
                    print(f"\n🔔 REMINDER: {row['event']} is in {days_left} day(s)!\n")

                row["last_notified"] = str(today)

            updated_rows.append(row)

    # Rewrite updated data
    with open(FILE_NAME, mode='w', newline='') as file:
        fieldnames = ["event", "date", "role", "last_notified"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)
