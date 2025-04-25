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

## Gameplay

# Card Game - Rules and Instructions

## Objective
Be the first to get rid of all the cards in your **pay-off pile** by playing them to the **centre stacks**.

## Setup
Each player has:
- A **pay-off pile** (cards face-down; only the top card is playable).
- A **hand** of up to 5 cards.
- Up to **4 side stacks** for temporary card storage.

The **centre area** can have up to **3 center stacks** at a time.

## How to Play
- Only the **top card** of your pay-off pile can be played at any time.
- To start a center stack, you must play an **Ace** (or a **King used as Ace**).
- Center stacks build **upward in order**: Ace ➔ 2 ➔ 3 ➔ … ➔ Queen.
- Suits **do not** matter.

You can:
- Play cards from your **hand**, **top of pay-off pile**, or **top of side stacks** to center stacks.
- **Discard** cards from your hand to side stacks (maximum of 4 side stacks).

You **cannot**:
- Move cards between side stacks.
- Move cards from a center stack elsewhere.
- Play pay-off cards to side stacks.

## Special Rules
- **Kings are wild**:
  - They can act as the next needed card on a center stack.
  - You can discard them to a side stack without committing their value.

- If you **finish all five cards in your hand** without discarding to a side stack:
  - Immediately **draw 5 more cards** and continue your turn.

- If you **complete** a center stack by playing a **Queen** (or a King acting as Queen):
  - Your opponent shuffles that completed stack into the stock.

## Turn Flow
1. If you have **fewer than 5 cards** in your hand, **draw cards** to bring your hand up to 5.
2. **Make as many plays as you can** to center stacks.
3. Once you **discard** to a side stack, **your turn ends**.
4. Players **alternate turns**.

## Winning
The first player to **empty their pay-off pile** wins!

## Starting Player
The player whose **pay-off pile top card is higher** goes first.

Have fun playing Spite and Malice, and happy coding!
