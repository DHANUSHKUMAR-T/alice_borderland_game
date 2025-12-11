from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import GameProgress
from app.games.card_engine import CARDS, SUITS, card_completed, check_phase_two_ready, mark_card_completed
from app import db

main = Blueprint("main", __name__)


# ---------------------------
# HOME PAGE
# ---------------------------
@main.route("/")
def home():
    return render_template("main/home.html", title="Welcome")


# ---------------------------
# DASHBOARD
# ---------------------------
@main.route("/dashboard")
@login_required
def dashboard():
    return render_template("main/dashboard.html", title="Dashboard")


# ---------------------------
# STORY PAGE (Placeholder)
# ---------------------------
@main.route("/story")
@login_required
def story():
    return render_template("main/story.html", title="Story")


# ---------------------------
# PLAY GAME (Phase Overview)
# ---------------------------
@main.route("/play")
@login_required
def play():
    progress = current_user.progress
    return render_template(
        "main/play.html",
        suits=SUITS,
        phase=progress.phase,
        title="Select Suit"
    )


# ---------------------------
# LIST CARDS FOR A SUIT
# ---------------------------
@main.route("/play/<suit>")
@login_required
def suit_cards(suit):

    if suit not in SUITS:
        return redirect(url_for("main.play"))

    progress = current_user.progress

    # Generate dictionary of card → completion
    cards_status = {}
    for card in CARDS:
        cards_status[card] = card_completed(progress, suit, card)

    return render_template(
        "main/suit_cards.html",
        suit=suit,
        cards=cards_status,
        title=f"{suit.title()} Cards"
    )


# ---------------------------
# LOAD SPECIFIC GAME PAGE
# ---------------------------
@main.route("/game/<suit>/<card>")
@login_required
def game_page(suit, card):

    if suit not in SUITS or card not in CARDS:
        return redirect(url_for("main.play"))

    return render_template(
        "games/generic_game.html",
        suit=suit,
        card=card,
        title=f"{suit.title()} {card}"
    )


from flask import request

# ---------------------------
# CARD COMPLETE
# ---------------------------
@main.route("/complete/<suit>/<card>", methods=["POST"])
@login_required
def complete_card(suit, card):

    if suit not in SUITS or card not in CARDS:
        return redirect(url_for("main.play"))

    progress = current_user.progress

    # Mark card completed
    mark_card_completed(progress, suit, card)
    db.session.commit()

    # Check if Phase 2 should unlock
    if check_phase_two_ready(progress):
        db.session.commit()

    return redirect(url_for("main.suit_cards", suit=suit))
