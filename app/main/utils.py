from app.games.card_engine import CARDS, SUITS, card_completed

def get_suit_progress(progress_obj, suit_name):
    """Returns a dictionary of card → complete status."""
    data = {}
    for card in CARDS:
        data[card] = card_completed(progress_obj, suit_name, card)
    return data


def get_phase(progress_obj):
    """Returns current phase of the user."""
    return progress_obj.phase
