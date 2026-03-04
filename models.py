from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Flashcard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.String(20))
    child_id = db.Column(db.Integer)
    message = db.Column(db.String(500))
# -----------------------------
# PARENT MODEL
# -----------------------------
class Parent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.String(20), unique=True, nullable=False)

    full_name = db.Column(db.String(100))
    child_name = db.Column(db.String(100))
    contact = db.Column(db.String(20))

    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))

    # SAVE PASSWORD
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # CHECK PASSWORD (LOGIN)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# -----------------------------
# CHILD MODEL
# -----------------------------
class Child(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(100))
    dob = db.Column(db.String(20))
    education = db.Column(db.String(100))

    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))

    # LINK TO PARENT
    parent_id = db.Column(
        db.String(20),
        db.ForeignKey('parent.parent_id')
    )

    # SAVE PASSWORD
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # CHECK PASSWORD (LOGIN)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)