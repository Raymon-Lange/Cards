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

### Objective
Be the first player to move all your cards from your play stack to the center stacks.

### Rules
- The game is played with two players, each with a 20-card stockpile.
- Cards are played from the stockpile to the center building piles, starting with an Ace and going up to a Queen.
- Kings are wild and can be used to substitute any card.
- The player with the highest-ranking face-up card in their stockpile plays first.
- Players draw cards to make a five-card hand and continue playing until their stockpile is empty.

### Building Foundations
- The first card on a center stack must be an Ace, followed by cards in ascending order.
- Cards can be played from the hand, discard piles, or play stack.

### Holding Stacks
- It's strategic to place multiple cards of the same numerical value on a holding stack pile.
- Cards in the holding stack can be in descending order.

### Game Ending
- The game ends when a player plays the last card of their pay-off pile to the center or when the stock runs out of cards.

Have fun playing Spite and Malice, and happy coding!
