from . import db
from flask_login import UserMixin

# -------------------------
# USER MODEL
# -------------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # Relationship to game progress
    progress = db.relationship("GameProgress", backref="user", uselist=False)


# -------------------------
# GAME PROGRESS MODEL
# Stores whether Ace–10 per suit is completed
# -------------------------
class GameProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Phase tracking
    phase = db.Column(db.Integer, default=1)  # 1 = Ace–10, 2 = J–Q–K

    # Spades
    spades_A = db.Column(db.Boolean, default=False)
    spades_2 = db.Column(db.Boolean, default=False)
    spades_3 = db.Column(db.Boolean, default=False)
    spades_4 = db.Column(db.Boolean, default=False)
    spades_5 = db.Column(db.Boolean, default=False)
    spades_6 = db.Column(db.Boolean, default=False)
    spades_7 = db.Column(db.Boolean, default=False)
    spades_8 = db.Column(db.Boolean, default=False)
    spades_9 = db.Column(db.Boolean, default=False)
    spades_10 = db.Column(db.Boolean, default=False)

    # Hearts
    hearts_A = db.Column(db.Boolean, default=False)
    hearts_2 = db.Column(db.Boolean, default=False)
    hearts_3 = db.Column(db.Boolean, default=False)
    hearts_4 = db.Column(db.Boolean, default=False)
    hearts_5 = db.Column(db.Boolean, default=False)
    hearts_6 = db.Column(db.Boolean, default=False)
    hearts_7 = db.Column(db.Boolean, default=False)
    hearts_8 = db.Column(db.Boolean, default=False)
    hearts_9 = db.Column(db.Boolean, default=False)
    hearts_10 = db.Column(db.Boolean, default=False)

    # Diamonds
    diamonds_A = db.Column(db.Boolean, default=False)
    diamonds_2 = db.Column(db.Boolean, default=False)
    diamonds_3 = db.Column(db.Boolean, default=False)
    diamonds_4 = db.Column(db.Boolean, default=False)
    diamonds_5 = db.Column(db.Boolean, default=False)
    diamonds_6 = db.Column(db.Boolean, default=False)
    diamonds_7 = db.Column(db.Boolean, default=False)
    diamonds_8 = db.Column(db.Boolean, default=False)
    diamonds_9 = db.Column(db.Boolean, default=False)
    diamonds_10 = db.Column(db.Boolean, default=False)

    # Clubs
    clubs_A = db.Column(db.Boolean, default=False)
    clubs_2 = db.Column(db.Boolean, default=False)
    clubs_3 = db.Column(db.Boolean, default=False)
    clubs_4 = db.Column(db.Boolean, default=False)
    clubs_5 = db.Column(db.Boolean, default=False)
    clubs_6 = db.Column(db.Boolean, default=False)
    clubs_7 = db.Column(db.Boolean, default=False)
    clubs_8 = db.Column(db.Boolean, default=False)
    clubs_9 = db.Column(db.Boolean, default=False)
    clubs_10 = db.Column(db.Boolean, default=False)
