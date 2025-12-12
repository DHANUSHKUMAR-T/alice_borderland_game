from flask import Blueprint, render_template, redirect, url_for, request,abort
from flask_login import login_required, current_user
from app.models import GameProgress
from app.games.card_engine import CARDS, SUITS, card_completed, check_phase_two_ready, mark_card_completed
from app import db
from app.story_data import CHAPTERS


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


# at top of main/routes.py add:
from flask import Blueprint, render_template, redirect, url_for, request, abort
from flask_login import login_required, current_user
from app.story_data import CHAPTERS

# ... (rest of file) ...

# Story index (list of chapters)
@main.route("/story")
@login_required
def story_index():
    # pass chapter list (only id & titles)
    chapters = [
        {"id": c["id"], "title": c["title"]["en"]} for c in CHAPTERS
    ]
    return render_template("main/story_index.html", chapters=chapters, title="Story Mode")

# Chapter page (single template used for all chapters)
@main.route("/story/<int:chapter_id>")
@login_required
def story_chapter(chapter_id):
    chapter = next((c for c in CHAPTERS if c["id"] == chapter_id), None)
    if not chapter:
        abort(404)
    # pass english text by default; template will select language via JS
    return render_template("main/story_chapter.html", chapter=chapter, title=chapter["title"]["en"])



# ---------------------------
# PLAY PAGE (Suit Selection)
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
# PHASE 1: CARDS FOR A SUIT
# ---------------------------
@main.route("/play/<suit>")
@login_required
def suit_cards(suit):

    if suit not in SUITS:
        return redirect(url_for("main.play"))

    progress = current_user.progress

    cards_status = {card: card_completed(progress, suit, card) for card in CARDS}

    all_done = all(cards_status[c] for c in CARDS)

    return render_template(
        "main/suit_cards.html",
        suit=suit,
        cards=cards_status,
        all_done=all_done,
        title=f"{suit.title()} Cards"
    )


# ---------------------------
# PHASE 1 GAME PAGE
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
# MARK A CARD COMPLETED
# ---------------------------
@main.route("/complete/<suit>/<card>", methods=["POST"])
@login_required
def complete_card(suit, card):

    if suit not in SUITS or card not in CARDS:
        return redirect(url_for("main.play"))

    progress = current_user.progress
    mark_card_completed(progress, suit, card)
    db.session.commit()

    # Unlock Phase 2 if all A–10 of all suits are finished
    if check_phase_two_ready(progress):
        progress.phase = 2
        db.session.commit()

    return redirect(url_for("main.suit_cards", suit=suit))


# ---------------------------
# PHASE 2: FACE CARDS PAGE
# ---------------------------
@main.route("/face-cards/<suit>")
@login_required
def face_cards(suit):

    progress = current_user.progress

    # 🔒 If Phase 1 not completed → block access
    if progress.phase < 2:
        return redirect(url_for("main.suit_cards", suit=suit))

    face_cards = ["J", "Q", "K"]

    return render_template(
        "main/face_cards.html",
        suit=suit,
        cards=face_cards,
        title=f"{suit.title()} Face Cards"
    )


# ---------------------------
# PHASE 2 FACE CARD GAME PAGE
# ---------------------------
@main.route("/face-game/<suit>/<card>")
@login_required
def face_game_page(suit, card):

    if card not in ["J", "Q", "K"]:
        return redirect(url_for("main.face_cards", suit=suit))

    return render_template(
        "games/face_game.html",
        suit=suit,
        card=card,
        title=f"{suit.title()} {card}"
    )
