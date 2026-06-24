# 🎴 Alice in Borderland Web Game

A Flask-based Alice in Borderland inspired survival game featuring card challenges, story progression, unlockable phases, face cards, and multiple endings.

---

# 📌 Project Overview

This project recreates the Alice in Borderland experience through interactive browser-based mini-games.

Players must complete challenges across all four suits:

- ♠ Spades — Physical Games
- ♥ Hearts — Psychological Games
- ♦ Diamonds — Intelligence Games
- ♣ Clubs — Teamwork Games

Successfully clearing all numbered cards unlocks the Face Cards and eventually the final Borderland ending.

---

# 🛠 Tech Stack

## Backend
- Python
- Flask
- Flask-Login
- SQLite

## Frontend
- HTML5
- CSS3
- JavaScript
- Jinja2 Templates
- Canvas API

---

# 📂 Project Structure

```text
app/
├── games/
├── main/
├── static/
│   ├── css/
│   ├── js/
│   ├── images/
├── templates/
│   ├── games/
│   └── main/
├── models.py
├── routes.py
├── story_data.py
└── __init__.py
🎮 Gameplay System
Phase 1 – Number Cards

Each suit contains:

A,2,3,4,5,6,7,8,9,10

Total:

40 Number Cards

Players must clear every numbered card to unlock Face Cards.

♠ Spades Challenges

Physical and endurance-based games.

Examples:

Memory Flash
Reaction Timer
Odd One Out
Moving Walls
Weight Shift
Limited Oxygen
Vertical Escape
Hunter's Hour

Focus:

Speed
Reflexes
Endurance
Survival
♥ Hearts Challenges

Psychological and emotional games.

Examples:

Emotion Match
Trust or Trap
Memory Betrayal
Silent Accusation
Emotional Trigger
Isolation
Last Connection

Focus:

Trust
Fear
Manipulation
Human Psychology
♦ Diamonds Challenges

Logic and intelligence games.

Examples:

Value Sort
Logic Lock
False Majority
Time Loop Logic
Probability Chamber
Encrypted Exit
Game Theory

Focus:

Math
Strategy
Reasoning
Pattern Recognition
♣ Clubs Challenges

Teamwork and coordination games.

Examples:

Reflex Gate
Threshold Check
Split Attention
Signal Chain
Bridge of Trust
Rotating Roles
Relay Maze
Human Network

Focus:

Coordination
Communication
Adaptability
Teamwork
👑 Phase 2 – Face Cards

Unlocked after all numbered cards are completed.

Jack

Intermediate boss-level challenges.

Queen

Psychological and strategic challenges.

King

Final suit challenge.

📖 Story Mode

Players can explore the Borderland through story chapters.

Features:

Character interactions
Multiple routes
Dialogue system
Mystery progression

Inspired by the atmosphere of Alice in Borderland while using original game content.

🎯 Progress System

Player progress is stored in SQLite.

Tracks:

Completed cards
Phase unlocks
Story progression
Face card completion
Ending requirements
🏁 Endings

The game contains multiple endings.

Good Ending

Return to the real world.

Requirements:

High completion rate
Positive choices
Neutral Ending

Return alone.

Requirements:

Mixed decisions
Average completion
Secret Ending

Hidden ending.

Requirements:

Discover secret clues
High performance
Joker Ending

Remain in Borderland.

Requirements:

Accept residency
Complete special requirements
🔓 Unlock System
Number Cards
↓
Face Cards
↓
Final Story
↓
Endings
🎨 Visual Style

Theme:

Black
Red
White
Neon Glow

Effects:

Screen shake
Danger overlays
Victory screens
Failure screens
Card reveal animations
🚀 Future Improvements
Advanced AI opponents
Multiplayer support
Voice acting
Mobile optimization
Achievement system
Leaderboards
✅ Development Goals
Complete all numbered cards
Complete all face cards
Story mode integration
Multiple endings
Progress tracking
Visual polish
Zero broken routes
Production-ready release

🎴 Welcome to the Borderland

Clear the games.

Survive the face cards.

Discover the truth.

Choose your ending.
