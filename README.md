# Spite and Malice

Welcome to the Cards repository! This project is a simple implementation of a card game. The code provides a foundation for various card games, and it currently includes the game "Spite and Malice." Feel free to explore, modify, and use the code for your own projects or to learn more about game development.

## Getting Started

To get started with this codebase, follow these steps:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Raymon-Lange/Cards.git


2.  **Install Pygame:**
  Ensure you have Python and [pip](https://pip.pypa.io/en/stable/installation/) installed. Then, install Pygame using the following command:
  ```bash
  pip install pygame-ce

  ```
3. **Run the Game:**


## Rules and Instructions

## Objective
Be the first to get rid of all the cards in your **goal pile** by playing them to the **Field **.

## Setup
Each player has:
- A **Goal pile** (cards face-down; only the top card is playable).
- A **hand** of up to 5 cards.
- Up to **4 discard stacks** for temporary card storage.

The **field area** can have up to **4 center stacks** at a time.

## How to Play
- Only the **top card** of your goal pile can be played at any time.
- To start a center stack, you must play an **Ace** (or a **King used as Ace**).
- Field stacks build **upward in order**: Ace ➔ 2 ➔ 3 ➔ … ➔ Queen.
- Suits **do not** matter.

You can:
- Play cards from your **hand**, **top of goal pile**, or **top of discard stacks** to field stacks.
- **Discard** cards from your hand to discard stacks (maximum of 4 discard stacks).

You **cannot**:
- Move cards between discard stacks.
- Move cards from a field stack elsewhere.
- Play goal cards to discard stacks.

## Special Rules
- **Kings are wild**:
  - They can act as the next needed card on a field stack.
  - You can discard them into a discard stack without committing their value.

- If you **finish all five cards in your hand** without discarding to a discard stack:
  - Immediately **draw 5 more cards** and continue your turn.

- If you **complete** a center stack by playing a **Queen** (or a King acting as Queen):
- The field stack will reset to zero, and cards will be shuffled into the deck

## Turn Flow
1. If you have **fewer than 5 cards** in your hand, **draw cards** to bring your hand up to 5.
2. **Make as many plays as you can** to field stacks.
3. Once you **discard** to a discard stack, **your turn ends**.
4. Players **alternate turns**.

## Winning
The first player to **empty their goal pile** wins!

## Starting Player
The player whose **goal pile top card is higher** goes first.

Have fun playing Spite and Malice, and happy coding!
