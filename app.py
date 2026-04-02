from flask import Flask, request, jsonify, render_template, redirect, session
from emotion import daily_emotion_analysis, save_daily_emotion, check_for_supportive_guidance
from chatbot import chatbot_reply
from flashcard import get_flashcard_status
import uuid
import csv
import os
from datetime import datetime, date
import pandas as pd
from models import db, Parent, Child


app = Flask(__name__)
app.secret_key = "teensense_super_secret_key"

# -------------------------------
# DATABASE CONFIG
# -------------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///teensense.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# -------------------------------
# HELPER: CHECK DAILY SUBMISSION
# -------------------------------
def already_submitted_today():
    try:
        df = pd.read_csv("daily_emotions.csv")
    except:
        return False

    today = date.today().isoformat()
    return any(df["date"] == today)

# -------------------------------
# HOME ROUTES
# -------------------------------
@app.route("/")
def home():
    return render_template("index.html")
@app.route("/choose-profile")
def choose_profile():
    return render_template("choose_profile.html")
# -------------------------------
# LOGIN
# -------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        parent = Parent.query.filter_by(email=email).first()
        if parent and parent.check_password(password):
            session.clear()
            session["parent_name"] = parent.full_name
            session["parent_id"] = parent.parent_id
            return redirect("/parent/dashboard")
        child = Child.query.filter_by(email=email).first()
        if child and child.check_password(password):
            session.clear()
            session["child_name"] = child.full_name
            session["parent_id"] = child.parent_id
            return redirect("/child/dashboard")
        return "Invalid Email or Password"
    return render_template("login.html")
# -------------------------------
# DASHBOARDS
# -------------------------------
@app.route("/parent/dashboard")
def parent_dashboard():
    if "parent_name" not in session:
        return redirect("/login")
    return render_template("parent_dashboard.html", parent_name=session["parent_name"])


@app.route("/child/dashboard")
def child_dashboard():
    if "child_name" not in session:
        return redirect("/login")
    return render_template("child_dashboard.html", child_name=session["child_name"])

# -------------------------------
# SIGNUP
# -------------------------------
@app.route("/parent/signup", methods=["GET", "POST"])
def parent_signup():
    if request.method == "POST":
        parent_id = "PRNT-" + uuid.uuid4().hex[:6].upper()
        new_parent = Parent(
            parent_id=parent_id,
            full_name=request.form["full_name"],
            child_name=request.form["child_name"],
            contact=request.form["contact"],
            email=request.form["email"]
        )
        new_parent.set_password(request.form["password"])
        db.session.add(new_parent)
        db.session.commit()
        return render_template("parent_success.html", parent_id=parent_id)
    return render_template("parent_signup.html")

@app.route("/child/signup", methods=["GET", "POST"])
def child_signup():
    if request.method == "POST":
        parent = Parent.query.filter_by(
            parent_id=request.form["parent_id"]
        ).first()
        if not parent:
            return "Invalid Parent ID!"
        new_child = Child(
            full_name=request.form["full_name"],
            dob=request.form["dob"],
            education=request.form["education"],
            parent_id=request.form["parent_id"],
            email=request.form["email"]
        )
        new_child.set_password(request.form["password"])
        db.session.add(new_child)
        db.session.commit()
        return render_template("child_success.html")
    return render_template("child_signup.html")
# -------------------------------
# 
# -------------------------------
# FLASHCARDS
# -------------------------------
FILE_NAME = "flashcards.csv"

def initialize_flashcard_file():
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                "id","sender","receiver","category","message",
                "response","status","sent_time","response_time"
            ])

def generate_id():
    initialize_flashcard_file()
    try:
        with open(FILE_NAME, mode='r') as file:
            reader = csv.DictReader(file)
            ids = [int(row["id"]) for row in reader if row["id"].isdigit()]
            return str(max(ids)+1) if ids else "1"
    except:
        return "1"


# -------------------------------
# PARENT FLASHCARDS
# -------------------------------
@app.route("/parent/flashcards")
def parent_flashcards():

    cards = [
        {"message": "How were your classes today? What did you learn?", "category": "check-in"},
        {"message": "What made you smile or feel happy today?", "category": "appreciation"},
        {"message": "Are you facing any difficulties with studies, assignments, or exams?", "category": "concern"},
        {"message": "Is there anything important event you want to remind or inform me about?", "category": "reminder"}
    ]

    for card in cards:
        status = get_flashcard_status(card["message"])

        card["sent"] = status.get("sent", False)
        card["response"] = status.get("response", "")
        card["status"] = status.get("status", "")
        card["can_resend"] = status.get("can_resend", False)

        # ✅ format time
        def format_time(t):
            if not t:
                return ""
            try:
                dt = datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                return dt.strftime("%d %b %Y, %I:%M %p")
            except:
                return t

        card["sent_time"] = format_time(status.get("sent_time"))
        card["response_time"] = format_time(status.get("response_time"))

    return render_template(
        "parent_flashcards.html",
        parent_name=session.get("parent_name", "Parent"),
        cards=cards
    )


# -------------------------------
# SEND FLASHCARD
# -------------------------------
@app.route("/send_flashcard", methods=["POST"])
def send_flashcard_web():
    if "parent_name" not in session:
        return redirect("/login")

    initialize_flashcard_file()

    with open(FILE_NAME, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            generate_id(),
            "parent",
            "teen",
            request.form["category"],
            request.form["message"],
            "",
            "sent",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # ✅ FIXED
            ""
        ])

    return redirect("/parent/flashcards")


# -------------------------------
# CHILD FLASHCARDS
# -------------------------------
@app.route("/teen/flashcards")
def teen_flashcards():
    if "child_name" not in session:
        return redirect("/login")

    initialize_flashcard_file()
    cards = []

    # ✅ DEFINE ONCE (outside loop)
    def format_time(t):
        if not t:
            return ""
        try:
            dt = datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%d %b %Y, %I:%M %p")
        except:
            return t

    with open(FILE_NAME, mode='r') as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row["receiver"] == "teen":

                cards.append({
                    "id": row["id"],
                    "message": row["message"],
                    "status": row["status"],
                    "response": row["response"],
                    "sent_time": format_time(row.get("sent_time"))
                })

    cards = list(reversed(cards))

    return render_template(
        "child_flashcards.html",
        cards=cards,
        child_name=session["child_name"]
    )
# -------------------------------
# RESPOND FLASHCARD
# -------------------------------
@app.route("/respond_flashcard", methods=["POST"])
def respond_flashcard():
    flashcard_id = request.form["id"]

    updated_rows = []

    with open(FILE_NAME, mode='r') as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row["id"] == flashcard_id:
                row["response"] = request.form["response"]
                row["status"] = "responded"
                row["response_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # ✅ NEW

            updated_rows.append(row)

    with open(FILE_NAME, mode='w', newline='') as file:
        fieldnames = [
            "id","sender","receiver","category","message",
            "response","status","sent_time","response_time"
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)

    return redirect("/teen/flashcards")
# -------------------------------
# REMINDERS (FINAL CORRECTED)
# -------------------------------
REMINDER_FILE = "reminders.csv"

# -------------------------------
# INITIALIZE FILE
# -------------------------------
def initialize_reminder_file():
    if not os.path.exists(REMINDER_FILE):
        with open(REMINDER_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                "id",
                "title",
                "date",
                "start",
                "end",
                "description",
                "created_by"
            ])


def generate_reminder_id():
    initialize_reminder_file()
    try:
        with open(REMINDER_FILE, mode='r') as file:
            reader = csv.DictReader(file)
            ids = [int(row["id"]) for row in reader if row["id"].isdigit()]
            return str(max(ids)+1) if ids else "1"
    except:
        return "1"


# -------------------------------
# CHILD VIEW REMINDERS
# -------------------------------
@app.route("/child/reminders", methods=["GET"])
def child_reminders():
    if "child_name" not in session:
        return redirect("/login")

    initialize_reminder_file()
    reminders = []

    try:
        with open(REMINDER_FILE, mode='r') as file:
            reader = csv.DictReader(file)

            for row in reader:
                # ✅ SHOW CHILD + SHARED
                if row.get("created_by") in [session["child_name"], "both"]:

                    raw_date = row.get("date", "")

                    try:
                        formatted_date = datetime.strptime(raw_date, "%Y-%m-%d").strftime("%Y-%m-%d")
                    except:
                        formatted_date = raw_date

                    reminders.append({
                        "title": row.get("title"),
                        "date": formatted_date,
                        "start": row.get("start"),
                        "end": row.get("end"),
                        "description": row.get("description")  # 🔥 IMPORTANT
                    })
    except:
        pass

    return render_template(
        "child_reminders.html",
        reminders=reminders,
        child_name=session["child_name"]
    )


# -------------------------------
# ADD REMINDER (CHILD → SMART ROUTING)
# -------------------------------
@app.route("/add_reminder", methods=["POST"])
def add_reminder():
    if "child_name" not in session:
        return redirect("/login")

    initialize_reminder_file()

    title = request.form.get("title")
    date = request.form.get("date")
    start = request.form.get("start")
    end = request.form.get("end")

    # ✅ VALIDATION
    if not title or not date:
        return "Title and Date are required!"

    # ✅ FIX DATE
    try:
        date = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
    except:
        return "Invalid date format!"

    # 🔥 SMART LOGIC
    title_lower = title.lower()

    if "exam" in title_lower:
        created_by = "both"   # 👈 visible to both

    elif "parent" in title_lower:
        created_by = "parent"  # 👈 FIXED (no session error)

    else:
        created_by = session["child_name"]   # 👈 only child

    # ✅ SAVE
    with open(REMINDER_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            generate_reminder_id(),
            title,
            date,
            start,
            end,
            "",
            created_by
        ])

    return redirect("/child/reminders")

# -------------------------------
# PARENT VIEW REMINDERS
# -------------------------------
@app.route("/parent/reminders")
def parent_reminders():
    if "parent_name" not in session:
        return redirect("/login")

    initialize_reminder_file()
    reminders = []

    with open(REMINDER_FILE, mode='r') as file:
        reader = csv.DictReader(file)

        for row in reader:
            # ✅ SHOW PARENT + SHARED
            if row.get("created_by") in [session["parent_name"], "both", "parent"]:

                reminders.append({
                    "title": row.get("title"),
                    "date": row.get("date"),
                    "start": row.get("start"),
                    "end": row.get("end"),
                    "description": row.get("description"),
                    "created_by": row.get("created_by")   # ✅ MUST BE PRESENT
                })

    return render_template(
        "parent_reminders.html",
        reminders=reminders,
        parent_name=session["parent_name"]
    )


# -------------------------------
# ADD REMINDER (PARENT)
# -------------------------------
@app.route("/add_parent_reminder", methods=["POST"])
def add_parent_reminder():
    if "parent_name" not in session:
        return redirect("/login")

    initialize_reminder_file()

    title = request.form.get("title")
    date = request.form.get("date")
    start = request.form.get("start")
    end = request.form.get("end")

    with open(REMINDER_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            generate_reminder_id(),
            title,
            date,
            start,
            end,
            "",
            session["parent_name"]
        ])

    return redirect("/parent/reminders")

# -------------------------------
# JOURNAL
# -------------------------------
# -------------------------------
# ALERT HISTORY FILE
# -------------------------------
ALERT_FILE = "alert_history.csv"

def initialize_alert_file():
    if not os.path.exists(ALERT_FILE):
        with open(ALERT_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                "message",
                "timestamp",
                "trigger_dates"
            ])
@app.route("/journal", methods=["GET", "POST"])
def journal():

    if "child_name" not in session:
        return redirect("/login")

    submitted_today = already_submitted_today()

    if request.method == "POST":

        if submitted_today:
            return render_template(
                "childjournal.html",
                message="⚠️ You already submitted today!",
                child_name=session["child_name"],
                submitted_today=True
            )

        text = request.form["journal_text"]

        result = daily_emotion_analysis([text])

        save_daily_emotion(
            result["final_emotion"],
            result["avg_confidence"],
            "journal",
            text
        )

        check_for_supportive_guidance()

        return render_template(
            "childjournal.html",
            message="Saved!",
            emotion=result["final_emotion"],
            child_name=session["child_name"],
            submitted_today=True
        )

    return render_template(
        "childjournal.html",
        child_name=session["child_name"],
        submitted_today=submitted_today
    )

# -------------------------------
# EMOJI MOOD
# -------------------------------
@app.route("/save_mood", methods=["POST"])
def save_mood():

    if "child_name" not in session:
        return jsonify({"status": "error"})

    if already_submitted_today():
        return jsonify({
            "status": "blocked",
            "message": "Already submitted today"
        })

    data = request.get_json()
    emotion = data.get("emotion")

    save_daily_emotion(emotion, 1.0, "emoji", "")

    check_for_supportive_guidance()

    return jsonify({"status": "success"})

# -------------------------------
# ALERTS (FIXED)
# -------------------------------
@app.route("/alerts")
def alerts():

    if "parent_name" not in session:
        return redirect("/login")

    latest_alert = None
    alert_history = []

    try:
        df = pd.read_csv("daily_emotions.csv")
        df.columns = df.columns.str.strip()

        emotions = df["emotion"].dropna().astype(str).str.strip()
        last = emotions.tail(3).tolist()

        negative = ["Sad", "Anxious", "Angry"]

        # ================= DETECTION =================
        if len(last) == 3 and all(e in negative for e in last):

            today = datetime.now().strftime("%Y-%m-%d")

            # ✅ LAST 3 TRIGGER DATES
            last_rows = df.tail(3)
            trigger_dates = ", ".join(last_rows["date"].tolist())

            initialize_alert_file()

            last_saved = None

            with open(ALERT_FILE, mode='r') as file:
                reader = list(csv.DictReader(file))
                if reader:
                    last_saved = reader[-1]

            # ✅ DUPLICATE CHECK
            should_save = True

            if last_saved:
                same_pattern = last_saved["trigger_dates"] == trigger_dates
                same_day = last_saved["timestamp"].startswith(today)

                if same_pattern or same_day:
                    should_save = False

            # ✅ SAVE ALERT
            if should_save:
                with open(ALERT_FILE, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([
                        "Child may be emotionally stressed.",
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        trigger_dates
                    ])

        # ================= LOAD ALERTS =================
        initialize_alert_file()

        with open(ALERT_FILE, mode='r') as file:
            reader = csv.DictReader(file)
            alert_history = list(reader)

        # latest first
        alert_history = list(reversed(alert_history))

        # ================= SPLIT LATEST + HISTORY =================
        if alert_history:
            latest_alert = alert_history[0]   # latest
            alert_history = alert_history[1:] # remaining

        # ================= FORMAT TIME =================
        def format_time(t):
            try:
                dt = datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                return dt.strftime("%d %b %Y, %I:%M %p")
            except:
                return t

        if latest_alert:
            latest_alert["timestamp"] = format_time(latest_alert["timestamp"])

        for alert in alert_history:
            alert["timestamp"] = format_time(alert["timestamp"])

    except Exception as e:
        print("ERROR:", e)

    return render_template(
        "alerts.html",
        parent_name=session["parent_name"],
        latest_alert=latest_alert,
        alert_history=alert_history
    )
# -------------------------------
# CHATBOT
# -------------------------------
@app.route("/api/parent_chat", methods=["POST"])
def parent_chat_api():
    reply = chatbot_reply(request.get_json().get("message"))
    return jsonify({"reply": reply})

# -------------------------------
# HELP
# -------------------------------
@app.route("/help")
def help_page():
    if "parent_name" not in session:
        return redirect("/login")

    return render_template(
        "help.html",
        parent_name=session["parent_name"]
    )
# -------------------------------
# LOGOUT
# -------------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)