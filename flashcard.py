import csv
import os
from datetime import datetime, timedelta

FILE_NAME = "flashcards.csv"

# -------------------------------
# INITIALIZE FILE
# -------------------------------
def initialize_flashcard_file():
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                "id", "sender", "receiver", "category",
                "message", "response", "status",
                "sent_time", "response_time"
            ])


# -------------------------------
# GENERATE UNIQUE ID
# -------------------------------
def generate_id():
    initialize_flashcard_file()

    try:
        with open(FILE_NAME, mode='r') as file:
            reader = csv.DictReader(file)
            ids = [int(row["id"]) for row in reader]
            return str(max(ids) + 1) if ids else "1"
    except:
        return "1"


# -------------------------------
# SEND FLASHCARD
# -------------------------------
def send_flashcard():
    initialize_flashcard_file()

    sender = input("Sender (parent/teen): ")
    receiver = input("Receiver (parent/teen): ")
    category = input("Category (support/appreciation/concern/check-in): ")
    message = input("Enter message: ")

    flashcard_id = generate_id()
    sent_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(FILE_NAME, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            flashcard_id,
            sender,
            receiver,
            category,
            message,
            "",
            "sent",
            sent_time,
            ""
        ])

    print("Flashcard sent successfully.\n")


# -------------------------------
# VIEW FLASHCARDS (WITH TIME)
# -------------------------------
def view_flashcards(role):
    initialize_flashcard_file()

    with open(FILE_NAME, mode='r') as file:
        reader = csv.DictReader(file)
        found = False

        for row in reader:
            if row["receiver"] == role:
                found = True

                print(f"\nID: {row['id']}")
                print(f"From: {row['sender']}")
                print(f"Category: {row['category']}")
                print(f"Message: {row['message']}")
                print(f"Status: {row['status']}")

                # ✅ Format Sent Time
                if row["sent_time"]:
                    sent_dt = datetime.strptime(row["sent_time"], "%Y-%m-%d %H:%M:%S")
                    print(f"Sent On: {sent_dt.strftime('%d %b %Y, %I:%M %p')}")

                # ✅ Format Response Time
                if row["response_time"]:
                    resp_dt = datetime.strptime(row["response_time"], "%Y-%m-%d %H:%M:%S")
                    print(f"Responded On: {resp_dt.strftime('%d %b %Y, %I:%M %p')}")

                # ✅ Show response
                if row["response"]:
                    print(f"Response: {row['response']}")

                print("-" * 40)

        if not found:
            print("No flashcards found.\n")


# -------------------------------
# RESPOND TO FLASHCARD
# -------------------------------
def respond_flashcard():
    initialize_flashcard_file()

    flashcard_id = input("Enter Flashcard ID to respond: ")
    response_text = input("Enter your response: ")

    updated_rows = []

    with open(FILE_NAME, mode='r') as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row["id"] == flashcard_id:
                row["response"] = response_text
                row["status"] = "responded"
                row["response_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print("Response recorded successfully.\n")

            updated_rows.append(row)

    with open(FILE_NAME, mode='w', newline='') as file:
        fieldnames = [
            "id", "sender", "receiver", "category",
            "message", "response", "status",
            "sent_time", "response_time"
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)


# -------------------------------
# GET FLASHCARD STATUS (SMART LOGIC)
# -------------------------------
from datetime import datetime, timedelta
import csv
import os

FILE_NAME = "flashcards.csv"

def get_flashcard_status(message):
    from datetime import datetime, timedelta
    import csv

    # ✅ FIX 1: If file doesn't exist → return safely
    if not os.path.exists(FILE_NAME):
        return {"sent": False}

    now = datetime.now()

    with open(FILE_NAME, mode='r') as file:
        reader = csv.DictReader(file)

        for row in reader:

            # ✅ FIX 2: Skip bad rows
            if "message" not in row:
                continue

            if row.get("message") == message and row.get("sender") == "parent":

                sent_time = datetime.strptime(row["sent_time"], "%Y-%m-%d %H:%M:%S")

                # ✅ Responded
                if row["status"] == "responded":
                    return {
                        "sent": True,
                        "status": "responded",
                        "response": row["response"],
                        "sent_time": row["sent_time"],
                        "response_time": row["response_time"],
                        "can_resend": True
                    }

                # ⏱ Time check
                time_diff = now - sent_time

                return {
                    "sent": True,
                    "status": "pending",
                    "response": "",
                    "sent_time": row["sent_time"],
                    "response_time": "",
                    "can_resend": time_diff.total_seconds() >= 86400
                }

    return {"sent": False}