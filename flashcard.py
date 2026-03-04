import csv
import os
from datetime import datetime

FILE_NAME = "flashcards.csv"

# Create file if not exists
def initialize_flashcard_file():
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["id", "sender", "receiver", "category", "message", "response", "status", "date"])


# Send Flashcard (Parent to Teen)
def send_flashcard():
    initialize_flashcard_file()

    sender = input("Sender (parent/teen): ")
    receiver = input("Receiver (parent/teen): ")
    category = input("Category (support/appreciation/concern/check-in): ")
    message = input("Enter message: ")

    flashcard_id = generate_id()

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
            datetime.today().date()
        ])

    print("Flashcard sent successfully.\n")


# View Flashcards for a Role
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
                print("-" * 30)

        if not found:
            print("No flashcards found.\n")


# Respond to Flashcard
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
                print("Response recorded successfully.\n")
            updated_rows.append(row)

    with open(FILE_NAME, mode='w', newline='') as file:
        fieldnames = ["id", "sender", "receiver", "category", "message", "response", "status", "date"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)


# Generate Unique ID
def generate_id():
    initialize_flashcard_file()

    try:
        with open(FILE_NAME, mode='r') as file:
            reader = csv.DictReader(file)
            ids = [int(row["id"]) for row in reader]
            return str(max(ids) + 1) if ids else "1"
    except:
        return "1"
