from flask import Flask, request, jsonify, render_template, redirect, session
from emotion import daily_emotion_analysis, save_daily_emotion, detect_emotion
from chatbot import chatbot_reply
import uuid
from models import db, Parent, Child
from werkzeug.security import check_password_hash

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

        # CHECK PARENT
        parent = Parent.query.filter_by(email=email).first()
        if parent and parent.check_password(password):
            session.clear()
            session["parent_name"] = parent.full_name
            session["parent_id"] = parent.parent_id
            return redirect("/parent/dashboard")

        # CHECK CHILD
        child = Child.query.filter_by(email=email).first()
        if child and child.check_password(password):
            session.clear()
            session["child_name"] = child.full_name
            session["parent_id"] = child.parent_id
            return redirect("/child/dashboard")

        return "Invalid Email or Password"

    return render_template("login.html")

# -------------------------------
# PARENT SIGNUP
# -------------------------------

@app.route("/parent/signup", methods=["GET", "POST"])
def parent_signup():

    if request.method == "POST":

        full_name = request.form["full_name"]
        child_name = request.form["child_name"]
        contact = request.form["contact"]
        email = request.form["email"]
        password = request.form["password"]

        parent_id = "PRNT-" + uuid.uuid4().hex[:6].upper()

        new_parent = Parent(
            parent_id=parent_id,
            full_name=full_name,
            child_name=child_name,
            contact=contact,
            email=email
        )

        new_parent.set_password(password)

        db.session.add(new_parent)
        db.session.commit()

        return render_template("parent_success.html", parent_id=parent_id)

    return render_template("parent_signup.html")

# -------------------------------
# CHILD SIGNUP
# -------------------------------

@app.route("/child/signup", methods=["GET", "POST"])
def child_signup():

    if request.method == "POST":

        full_name = request.form["full_name"]
        dob = request.form["dob"]
        education = request.form["education"]
        parent_id = request.form["parent_id"]
        email = request.form["email"]
        password = request.form["password"]

        parent = Parent.query.filter_by(parent_id=parent_id).first()
        if not parent:
            return "Invalid Parent ID!"

        new_child = Child(
            full_name=full_name,
            dob=dob,
            education=education,
            parent_id=parent_id,
            email=email
        )

        new_child.set_password(password)

        db.session.add(new_child)
        db.session.commit()

        return render_template("child_success.html")

    return render_template("child_signup.html")

# -------------------------------
# DASHBOARDS
# -------------------------------

@app.route("/parent/dashboard")
def parent_dashboard():
    if "parent_name" not in session:
        return redirect("/login")

    return render_template(
        "parent_dashboard.html",
        parent_name=session["parent_name"]
    )

@app.route("/child/dashboard")
def child_dashboard():
    if "child_name" not in session:
        return redirect("/login")

    return render_template(
        "child_dashboard.html",
        child_name=session["child_name"]
    )
@app.route("/flashcards")
def flashcards():

    if "parent_name" not in session:
        return redirect("/login")

    return render_template(
        "parent_flashcards.html",
        parent_name=session["parent_name"]
    )
# -------------------------------
# JOURNAL
# -------------------------------

@app.route("/journal", methods=["GET", "POST"])
def journal():

    if "child_name" not in session:
        return redirect("/login")

    if request.method == "POST":

        journal_text = request.form["journal_text"]

        # Detect emotion
        emotion = detect_emotion(journal_text)

        # Save alert for parent
        session["last_alert"] = f"Child {session['child_name']} emotion detected: {emotion}"

        return render_template(
            "childjournal.html",
            message="Journal saved successfully!",
            emotion=emotion,
            child_name=session["child_name"]
        )

    return render_template(
        "childjournal.html",
        child_name=session["child_name"]
    )

# -------------------------------
# ALERTS (PARENT)
# -------------------------------

@app.route("/alerts")
def alerts():

    if "parent_name" not in session:
        return redirect("/login")

    alert_msg = session.get("last_alert")

    return render_template(
        "alerts.html",
        parent_name=session["parent_name"],
        alert_message=alert_msg
    )

# -------------------------------
# CHATBOT API
# -------------------------------

@app.route("/api/parent_chat", methods=["POST"])
def parent_chat_api():
    data = request.get_json()
    user_message = data.get("message")
    reply = chatbot_reply(user_message)
    return jsonify({"reply": reply})

# -------------------------------
# LOGOUT
# -------------------------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")



# -------------------------------
# RUN SERVER
# -------------------------------

#if __name__ == "__main__":
    #app.run(debug=True)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, threaded=False)