import jinja2
from flask import Blueprint, render_template, redirect, url_for, request, abort, flash
from flask_login import login_required, current_user
from app.models import GameProgress
from app.games.card_engine import CARDS, SUITS, card_completed, check_phase_two_ready, mark_card_completed
from app import db
from app.story_data import CHAPTERS

main = Blueprint("main", __name__)

CHAPTER_CHOICES = {
    1: {
        "question": "Choose your initial strategy in the empty Shibuya streets:",
        "options": [
            {"id": "defend", "text": "Search for weapons and prepare for a direct fight"},
            {"id": "scout", "text": "Search for maps and map out high ground / escape routes"}
        ]
    },
    2: {
        "question": "Whose survival style do you rely on for this game?",
        "options": [
            {"id": "aggression", "text": "Trust Karube's physical aggression and tactical pressure"},
            {"id": "caution", "text": "Follow Chota's analytical caution and stay back"}
        ]
    },
    3: {
        "question": "Usagi opens up about her past. How do you respond?",
        "options": [
            {"id": "comfort", "text": "Hold her close and promise you will survive together"},
            {"id": "grief", "text": "Share your grief for Chota and Karube, binding your mutual pain"}
        ]
    },
    4: {
        "question": "How do you navigate the factions inside Hatter's Beach?",
        "options": [
            {"id": "power", "text": "Align with Hatter's inner circle to secure resource access"},
            {"id": "shadows", "text": "Remain neutral and observe the executives from the shadows"}
        ]
    },
    5: {
        "question": "How do you face the lethal Face Card games?",
        "options": [
            {"id": "fight", "text": "Fight head-on with pure athletic will"},
            {"id": "outsmart", "text": "Observe and dismantle their rules from within"}
        ]
    },
    6: {
        "question": "Mira offers you a tea party. She offers comfort in this fake world. Choose your destiny:",
        "options": [
            {"id": "dream", "text": "Accept the illusion and stay in the peaceful garden (Residency)"},
            {"id": "reality", "text": "Reject the residency and fight to wake up to reality"}
        ]
    }
}

CHAPTER_REQUIREMENTS = {
    1: 0,
    2: 5,
    3: 15,
    4: 25,
    5: 40,
    6: 45,
    7: 52
}

def count_completed_cards(progress):
    suits = ["spades", "hearts", "diamonds", "clubs"]
    cards = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    count = 0
    for s in suits:
        for c in cards:
            if getattr(progress, f"{s}_{c}", False):
                count += 1
    return count

def get_choices_dict(choices_str):
    choices = {}
    if not choices_str:
        return choices
    for pair in choices_str.split(","):
        if ":" in pair:
            ch_id, val = pair.split(":", 1)
            try:
                choices[int(ch_id)] = val
            except ValueError:
                pass
    return choices

def save_choice(progress, chapter_id, choice_val):
    choices = get_choices_dict(progress.story_choices)
    choices[chapter_id] = choice_val
    progress.story_choices = ",".join(f"{ch}:{val}" for ch, val in choices.items())


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
    progress = current_user.progress
    completed_count = count_completed_cards(progress)
    
    chapters_data = []
    for c in CHAPTERS:
        req = CHAPTER_REQUIREMENTS.get(c["id"], 0)
        unlocked = completed_count >= req
        chapters_data.append({
            "id": c["id"],
            "title": c["title"]["en"],
            "required": req,
            "unlocked": unlocked
        })
    return render_template(
        "main/story_index.html", 
        chapters=chapters_data, 
        completed_count=completed_count,
        title="Story Mode"
    )


# ---------------------------
# STORY MODE - Chapter Reader
# ---------------------------
@main.route("/story/<int:chapter_id>")
@login_required
def story_chapter(chapter_id):
    progress = current_user.progress
    completed_count = count_completed_cards(progress)
    
    req = CHAPTER_REQUIREMENTS.get(chapter_id, 0)
    if completed_count < req:
        flash(f"Chapter {chapter_id} is locked. Complete {req} cards to unlock (Current: {completed_count}).")
        return redirect(url_for("main.story_index"))
        
    chapter = next((c for c in CHAPTERS if c["id"] == chapter_id), None)
    if not chapter:
        abort(404)
        
    # Choice details
    choice_info = CHAPTER_CHOICES.get(chapter_id, None)
    user_choices = get_choices_dict(progress.story_choices)
    user_choice = user_choices.get(chapter_id, None)
    
    user_choice_text = ""
    if user_choice and choice_info:
        opt = next((o for o in choice_info["options"] if o["id"] == user_choice), None)
        if opt:
            user_choice_text = opt["text"]

    # If it is chapter 7 and all cards completed, show the final fate button
    show_fate_btn = (chapter_id == 7 and completed_count == 52)
            
    return render_template(
        "main/story_chapter.html", 
        chapter=chapter, 
        choice_info=choice_info,
        user_choice=user_choice,
        user_choice_text=user_choice_text,
        show_fate_btn=show_fate_btn,
        title=chapter["title"]["en"]
    )


# ---------------------------
# STORY MODE - Record Choice
# ---------------------------
@main.route("/story/choose/<int:chapter_id>", methods=["POST"])
@login_required
def story_choose(chapter_id):
    choice_val = request.form.get("choice")
    if not choice_val:
        return redirect(url_for("main.story_chapter", chapter_id=chapter_id))
        
    progress = current_user.progress
    save_choice(progress, chapter_id, choice_val)
    db.session.commit()
    
    return redirect(url_for("main.story_chapter", chapter_id=chapter_id))



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

    template_name = f"games/{suit}_{card}.html"
    try:
        return render_template(
            template_name,
            suit=suit,
            card=card,
            title=f"{suit.title()} {card}"
        )
    except jinja2.exceptions.TemplateNotFound:
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
    
@main.route("/game/spades/6")
@login_required
def spades_6():
    return render_template("games/spades_6.html",
                           title="Spades 6 – Moving Walls")
    
@main.route("/game/spades/7")
@login_required
def spades_7():
    return render_template("games/spades_7.html",
                           title="Spades 7 – Weight Shift")
    
@main.route("/game/spades/8")
@login_required
def spades_8():
    return render_template("games/spades_8.html",
                           title="Spades 8 – Limited Oxygen")

@main.route("/game/spades/9")
@login_required
def spades_9():
    return render_template("games/spades_9.html",
                           title="Spades 9 – Vertical Escape")
    
@main.route("/game/spades/10")
@login_required
def spades_10():
    return render_template("games/spades_10.html",
                           title="Spades 10 – Hunter’s Hour")

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
    
@main.route("/game/hearts/6")
@login_required
def hearts_6():
    return render_template("games/hearts_6.html",
                           title="Hearts 6 – Memory Betrayal")

@main.route("/game/hearts/7")
@login_required
def hearts_7():
    return render_template("games/hearts_7.html",
                           title="Hearts 7 – Silent Accusation")
@main.route("/game/hearts/8")
@login_required
def hearts_8():
    return render_template("games/hearts_8.html",
                           title="Hearts 8 – Emotional Trigger")
@main.route("/game/hearts/9")
@login_required
def hearts_9():
    return render_template("games/hearts_9.html",
                           title="Hearts 9 – Isolation")
    
@main.route("/game/hearts/10")
@login_required
def hearts_10():
    return render_template("games/hearts_10.html",
                           title="Hearts 10 – Last Connection")

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
    
@main.route("/game/diamonds/6")
@login_required
def diamonds_6():
    return render_template("games/diamonds_6.html",
                           title="Diamonds 6 – False Majority")
    
@main.route("/game/diamonds/7")
@login_required
def diamonds_7():
    return render_template("games/diamonds_7.html",
                           title="Diamonds 7 – Time Loop Logic")
    
@main.route("/game/diamonds/8")
@login_required
def diamonds_8():
    return render_template("games/diamonds_8.html",
                           title="Diamonds 8 – Probability Chamber")  
    
@main.route("/game/diamonds/9")
@login_required
def diamonds_9():
    return render_template("games/diamonds_9.html",
                           title="Diamonds 9 – Encrypted Exit")  
    
@main.route("/game/diamonds/10")
@login_required
def diamonds_10():
    return render_template("games/diamonds_10.html",
                           title="Diamonds 10 – Game Theory")  
    
@main.route("/game/clubs/A")
@login_required
def clubs_A():
    return render_template("games/clubs_A.html",
                           title="♣ Clubs A – Reflex Gate")
    
@main.route("/game/clubs/2")
@login_required
def clubs_2():
    return render_template("games/clubs_2.html",
                           title="♣ Clubs 2 – Threshold Check")
    
@main.route("/game/clubs/3")
@login_required
def clubs_3():
    return render_template("games/clubs_3.html",
                           title="♣ Clubs 3 – Split Attention")
    
@main.route("/game/clubs/4")
@login_required
def clubs_4():
    return render_template("games/clubs_4.html",
                           title="♣ Clubs 4 – Stillness Check")
    
@main.route("/game/clubs/5")
@login_required
def clubs_5():
    return render_template("games/clubs_5.html",
                           title="♣ Clubs 5 – Inner Record")
    
@main.route("/game/clubs/6")
@login_required
def clubs_6():
    return render_template("games/clubs_6.html",
                           title="♣ Clubs 6 – Stillness Check")
    

@main.route("/game/clubs/7")
@login_required
def clubs_7():
    return render_template("games/clubs_7.html",
                           title="♣ Clubs 7 – Bridge of Trust")

@main.route("/game/clubs/8")
@login_required
def clubs_8():
    return render_template("games/clubs_8.html",
                           title="♣ Clubs 8 – Rotating Roles")

@main.route("/game/clubs/9")
@login_required
def clubs_9():
    return render_template("games/clubs_9.html",
                           title="♣ Clubs 9 – Relay Maze")

@main.route("/game/clubs/10")
@login_required
def clubs_10():
    return render_template("games/clubs_10.html",
                           title="♣ Clubs 10 – Human Network")

# ---------------------------
# MARK CARD COMPLETED
# ---------------------------
@main.route("/complete/<suit>/<card>", methods=["POST"])
@login_required
def complete_card(suit, card):

    if suit not in SUITS or (card not in CARDS and card not in ["J", "Q", "K"]):
        return redirect(url_for("main.play"))

    progress = current_user.progress
    mark_card_completed(progress, suit, card)
    db.session.commit()

    # unlock phase 2 if all 40 cards done
    if check_phase_two_ready(progress):
        progress.phase = 2
        db.session.commit()

    if card in ["J", "Q", "K"]:
        return redirect(url_for("main.face_cards", suit=suit))
    return redirect(url_for("main.suit_cards", suit=suit))


# ---------------------------
# PHASE 2 — FACE CARDS
# ---------------------------
@main.route("/face-cards/<suit>")
@login_required
def face_cards(suit):

    if suit not in SUITS:
        return redirect(url_for("main.play"))

    progress = current_user.progress

    # Check if THIS SUIT is fully completed
    suit_cards_status = [
        card_completed(progress, suit, card)
        for card in CARDS
    ]

    if not all(suit_cards_status):
        return redirect(url_for("main.suit_cards", suit=suit))

    face_cards_status = {
        card: card_completed(progress, suit, card)
        for card in ["J", "Q", "K"]
    }

    return render_template(
        "main/face_cards.html",
        suit=suit,
        cards=face_cards_status,
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

    template_name = f"games/{suit}_{card}.html"
    try:
        return render_template(
            template_name,
            suit=suit,
            card=card,
            title=f"{suit.title()} {card}"
        )
    except jinja2.exceptions.TemplateNotFound:
        return render_template(
            "games/face_game.html",
            suit=suit,
            card=card,
            title=f"{suit.title()} {card}"
        )


# ---------------------------
# FINAL ENDING MODE
# ---------------------------
@main.route("/ending")
@login_required
def ending():
    progress = current_user.progress
    completed_count = count_completed_cards(progress)
    
    if completed_count < 40:
        flash("You must complete more cards to reach an ending!")
        return redirect(url_for("main.dashboard"))
        
    user_choices = get_choices_dict(progress.story_choices)
    ch5_choice = user_choices.get(5, "")
    ch6_choice = user_choices.get(6, "")
    
    ending_type = "neutral"
    
    if completed_count == 52:
        if ch6_choice == "reality":
            if ch5_choice == "outsmart" and progress.total_retries < 3:
                ending_type = "secret"
            else:
                ending_type = "good"
        elif ch6_choice == "dream":
            ending_type = "joker"
    else:
        ending_type = "neutral"
        
    return render_template(f"endings/{ending_type}.html", title=f"{ending_type.upper()} ENDING")

