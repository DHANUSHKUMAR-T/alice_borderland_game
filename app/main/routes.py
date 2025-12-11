from flask import Blueprint, render_template, redirect, url_for, request
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
# STORY PAGE
# ---------------------------
@main.route("/story")
@login_required
def story():
    return render_template("main/story.html", title="Story")


# ---------------------------
# PLAY GAME main page (Suit selection)
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
# PHASE 1: LIST CARDS FOR A SUIT
# ---------------------------
@main.route("/play/<suit>")
@login_required
def suit_cards(suit):

    if suit not in SUITS:
        return redirect(url_for("main.play"))

    progress = current_user.progress

    # Build card → completed dictionary
    cards_status = {}
    for card in CARDS:
        cards_status[card] = card_completed(progress, suit, card)

    # Check if all A–10 are completed
    all_done = all(cards_status[c] for c in CARDS)

    return render_template(
        "main/suit_cards.html",
        suit=suit,
        cards=cards_status,
        all_done=all_done,      # 🔥 Needed for Face-Card button unlock
        title=f"{suit.title()} Cards"
    )


# ---------------------------
# LOAD INDIVIDUAL GAME PAGE
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


# ---------------------------
# MARK CARD COMPLETED
# ---------------------------
@main.route("/complete/<suit>/<card>", methods=["POST"])
@login_required
def complete_card(suit, card):

    if suit not in SUITS or card not in CARDS:
        return redirect(url_for("main.play"))

    progress = current_user.progress

    # Mark the card as completed
    mark_card_completed(progress, suit, card)
    db.session.commit()

    # If all cards of ALL suits are done, unlock Phase 2
    if check_phase_two_ready(progress):
        progress.phase = 2
        db.session.commit()

    return redirect(url_for("main.suit_cards", suit=suit))


# ---------------------------
# FACE CARDS PAGE (Phase 2)
# ---------------------------
@main.route("/face-cards/<suit>")
@login_required
def face_cards(suit):

    progress = current_user.progress

    # 🔒 Block access if Phase 1 is not completed
    if progress.phase < 2:
        return redirect(url_for("main.suit_cards", suit=suit))

    face_cards = ["J", "Q", "K"]

    return render_template(
        "main/face_cards.html",
        suit=suit,
        cards=face_cards,
        title=f"{suit.title()} Face Cards"
    )
