from flask import Blueprint, render_template, redirect, url_for, request, abort
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


# ---------------------------
# STORY MODE - Chapter List
# ---------------------------
@main.route("/story")
@login_required
def story_index():
    chapters = [{"id": c["id"], "title": c["title"]["en"]} for c in CHAPTERS]
    return render_template("main/story_index.html", chapters=chapters, title="Story Mode")


# ---------------------------
# STORY MODE - Chapter Reader
# ---------------------------
@main.route("/story/<int:chapter_id>")
@login_required
def story_chapter(chapter_id):
    chapter = next((c for c in CHAPTERS if c["id"] == chapter_id), None)
    if not chapter:
        abort(404)
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
# PHASE 1 -- CARDS INSIDE SUIT
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
# GENERIC GAME PAGE
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
# CUSTOM GAME: SPADES A
# ---------------------------
@main.route("/game/spades/A")
@login_required
def spades_A():
    return render_template(
        "games/spades_A.html",
        title="Spades A – Memory Flash Game"
    )

@main.route("/game/spades/2")
@login_required
def spades_2():
    return render_template("games/spades_2.html", title="Spades 2 – Reaction Timer")

@main.route("/game/spades/3")
@login_required
def spades_3():
    return render_template("games/spades_3.html", title="Spades 3 – Odd One Out")

@main.route("/game/spades/4")
@login_required
def spades_4():
    return render_template("games/spades_4.html", title="Spades 4 – Big Even/Odd Finder")

@main.route("/game/spades/5")
@login_required
def spades_5():
    return render_template("games/spades_5.html",
                           title="Spades 5 – Color Decision Game")

@main.route("/game/hearts/A")
@login_required
def hearts_A():
    return render_template("games/hearts_A.html",
                           title="Hearts A – Emotion Match")
    
@main.route("/game/hearts/2")
@login_required
def hearts_2():
    return render_template("games/hearts_2.html",
                           title="Hearts 2 – Trust or Trap")

@main.route("/game/hearts/3")
@login_required
def hearts_3():
    return render_template("games/hearts_3.html",
                           title="Hearts 3 – Heartbeat Rhythm")
    
@main.route("/game/hearts/4")
@login_required
def hearts_4():
    return render_template("games/hearts_4.html",
                           title="Hearts 4 – Moral Choice")

@main.route("/game/hearts/5")
@login_required
def hearts_5():
    return render_template("games/hearts_5.html",
                           title="Hearts 5 – Focus Under Emotion")
    
@main.route("/game/diamonds/A")
@login_required
def diamonds_A():
    return render_template("games/diamonds_A.html",
                           title="Diamonds A –  Value Sort")

@main.route("/game/diamonds/2")
@login_required
def diamonds_2():
    return render_template("games/diamonds_2.html",
                           title="Diamonds 2 – Logic Lock")
    
@main.route("/game/diamonds/3")
@login_required
def diamonds_3():
    return render_template("games/diamonds_3.html",
                           title="Diamonds 3 – Pattern Break")
    
@main.route("/game/diamonds/4")
@login_required
def diamonds_4():
    return render_template("games/diamonds_4.html",
                           title="Diamonds 4 – Risk vs Reward")

@main.route("/game/diamonds/5")
@login_required
def diamonds_5():
    return render_template("games/diamonds_5.html",
                           title="Diamonds 5 – Silence Test")
    
@main.route("/game/clubs/A")
@login_required
def clubs_A():
    return render_template("games/clubs_A.html",
                           title="Clubs A – Reflex Gate")
    
@main.route("/game/clubs/2")
@login_required
def clubs_2():
    return render_template("games/clubs_2.html",
                           title="Clubs A – Reflex Gate")
    



# ---------------------------
# MARK CARD COMPLETED
# ---------------------------
@main.route("/complete/<suit>/<card>", methods=["POST"])
@login_required
def complete_card(suit, card):

    if suit not in SUITS or card not in CARDS:
        return redirect(url_for("main.play"))

    progress = current_user.progress
    mark_card_completed(progress, suit, card)
    db.session.commit()

    # unlock phase 2 if all 40 cards done
    if check_phase_two_ready(progress):
        progress.phase = 2
        db.session.commit()

    return redirect(url_for("main.suit_cards", suit=suit))


# ---------------------------
# PHASE 2 — FACE CARDS
# ---------------------------
@main.route("/face-cards/<suit>")
@login_required
def face_cards(suit):

    progress = current_user.progress

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
# PHASE 2 — FACE GAME PAGE
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
