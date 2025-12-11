# -------------------------
# CARD ENGINE (Backend)
# -------------------------

SUITS = ["spades", "hearts", "diamonds", "clubs"]
CARDS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10"]

def get_all_cards():
    """Return full Phase 1 deck (Ace–10 for each suit)."""
    deck = []
    for suit in SUITS:
        for card in CARDS:
            deck.append({"suit": suit, "card": card})
    return deck


def card_completed(progress_obj, suit, card):
    """Return True/False if a card is completed."""
    field = f"{suit}_{card}"
    return getattr(progress_obj, field)


def mark_card_completed(progress_obj, suit, card):
    """Mark a card as completed and commit later in route."""
    field = f"{suit}_{card}"
    setattr(progress_obj, field, True)


def check_phase_two_ready(progress_obj):
    """Checks if all Ace–10 cards are completed."""
    all_suits = [
        "spades", "hearts", "diamonds", "clubs"
    ]

    for suit in all_suits:
        for card in CARDS:
            field = f"{suit}_{card}"
            if not getattr(progress_obj, field):
                return False  # Still missing cards

    # All cards completed → Phase 2 unlocks
    progress_obj.phase = 2
    return True
