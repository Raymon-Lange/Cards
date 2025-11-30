#!/usr/bin/env python3
"""
Simple agent that connects to the Cards server and plays moves.
This agent uses a greedy-then-random policy:
- If there's a legal move for a centre stack for a card from hand/goal/discard, play it.
- Otherwise discard the lowest priority card in hand to a discard pile (0..3).
- If no cards and the server didn't deal automatically: call deal::

Usage
-----
1. Start the server:
   export SDL_VIDEODRIVER=dummy
   python3 Server.py
2. Run an agent:
   python3 Agent.py

The agent will connect as a regular client and issue commands the same way the GUI client does.
"""

import argparse
import random
import time
import logging
import os

# Make sure pygame runs headless when Game module imports pygame
os.environ.setdefault('SDL_VIDEODRIVER', os.environ.get('SDL_VIDEODRIVER', 'dummy'))

from Network import Network
from Game import Card

logger = logging.getLogger("Agent")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class Agent:
    def __init__(self, policy='greedy', retry_delay=0.05, max_retries=20):
        self.n = Network(max_retries=max_retries, retry_delay=retry_delay)
        self.player_id = self.n.getId()
        self.policy = policy
        logger.info(f"Agent connected as player {self.player_id}")

    def get_board(self):
        try:
            return self.n.send("get")
        except Exception as e:
            logger.error(f"Error requesting board: {e}")
            return None

    def ranks_index(self, rank, deck):
        try:
            return deck.ranks.index(rank)
        except Exception:
            return -1

    def find_moves(self, board):
        """Return list of (action, value, location) legal moves based on current board state.
        We try to simulate the move validation logic in `Game.Board.move` and `playCard`.
        """
        moves = []
        # Shortcuts
        my_player_id = int(self.player_id) if self.player_id is not None else 0
        deck = board.deck

        # Determine our personal player object
        player = board.playerOne if my_player_id == 0 else board.playerTwo

        # Helper to append move
        def append_move(act, card, loc, source=None):
            # attach source metadata (goal/hand/discard_N) so we can log and prefer it in pick_move
            moves.append((act, str(card), str(loc), source))

        # For each field location, check if card can be moved
        # Candidate order: check goal pile first, then hand, then each discard pile
        for field_idx, field_pile in enumerate(board.field):
            sources = [('goal', player.goal), ('hand', player.hand)] + [(f'discard_{i}', player.discard[i]) for i in range(len(player.discard))]
            for card_source, source_list in sources:
                src_cards = source_list
                if not src_cards:
                    continue

                # Goal and discard piles: only top-most card is playable; hand: any card
                if card_source == 'goal' or card_source.startswith('discard_'):
                    candidates = [src_cards[-1]]
                else:
                    candidates = list(src_cards)

                for card in candidates:
                    if len(field_pile) == 0:
                        # Empty pile, only Ace or King can start the pile
                        if card.rank == 'Ace' or card.rank == 'King':
                            append_move('move', card, field_idx, source=card_source if card_source is not None else 'hand')
                    else:
                        # need to check top card value; Board.move uses deck.ranks index and counts
                        top_count = len(field_pile) - 1
                        # Board.move determines if ranks.index(card.rank) - cardCount == 1 or King
                        if card.rank == 'King' or deck.ranks.index(card.rank) - top_count == 1:
                            append_move('move', card, field_idx, source=card_source if card_source is not None else 'hand')

        # If no moves, consider discarding a hand card to any discard pile (0..3)
        if len(player.hand) > 0:
            for card in player.hand:
                for d in range(4):
                    append_move('discard', card, d, source='hand')
                    # Prefer lower-numbered discard pile; break to avoid flooding
                    break
                break

        # If no moves at all, consider 'deal' to draw cards if allowed
        if len(moves) == 0:
            append_move('deal', '', 0, source=None)

        return moves

    def pick_move(self, moves, board):
        if not moves:
            return None
        if self.policy == 'random':
            choice = random.choice(moves)
            logger.debug(f"Agent selected (random) move {choice[0]}:{choice[1]}:{choice[2]} from {choice[3]}")
            return choice
        # greedy: prefer moves of type 'move' over discard/deal
        move_candidates = [m for m in moves if m[0] == 'move']
        if move_candidates:
            # Prefer moves by origin: goal > hand > discard
            goal_moves = [m for m in move_candidates if m[3] == 'goal']
            if goal_moves:
                choice = random.choice(goal_moves)
                logger.debug(f"Agent selected goal move {choice[0]}:{choice[1]}:{choice[2]} from {choice[3]}")
                return choice
            hand_moves = [m for m in move_candidates if m[3] == 'hand']
            if hand_moves:
                choice = random.choice(hand_moves)
                logger.debug(f"Agent selected hand move {choice[0]}:{choice[1]}:{choice[2]} from {choice[3]}")
                return choice
            discard_moves = [m for m in move_candidates if m[3] and m[3].startswith('discard_')]
            if discard_moves:
                choice = random.choice(discard_moves)
                logger.debug(f"Agent selected discard move {choice[0]}:{choice[1]}:{choice[2]} from {choice[3]}")
                return choice
        # else discard
        discards = [m for m in moves if m[0] == 'discard']
        if discards:
            choice = random.choice(discards)
            logger.debug(f"Agent selected discard action {choice[0]}:{choice[1]}:{choice[2]} from {choice[3]}")
            return choice
        # fallback: return the first move (strip source if present)
        first = moves[0]
        logger.debug(f"Agent selected fallback move {first[0]}:{first[1]}:{first[2]} from {first[3]}")
        return first

    def send_move(self, action, value, location, source=None):
        data = f"{action}:{value}:{location}" if value is not None else f"{action}::"
        # source indicates whether this card came from 'goal', 'hand', or 'discard_N'
        origin = source or 'unknown'
        # Describe the target (field or discard pile) in a human-friendly way
        target_desc = f"field {location}" if action == 'move' else (f"discard {location}" if action == 'discard' else action)
        logger.info(f"Player {self.player_id} sending move: {data} (origin={origin}, target={target_desc})")
        try:
            board = self.n.send(data)
            return board
        except Exception as e:
            logger.error(f"Error sending move: {e}")
            return None

    def play_loop(self, loop_delay=1.0):
        try:
            while True:
                board = self.get_board()
                if board is None:
                    time.sleep(loop_delay)
                    continue

                if getattr(board, 'winner', None) is not None:
                    # Game finished
                    logger.info(f"Game ended. Winner: {board.winner}")
                    break

                # It's our turn? board.currentTurn == my id
                my_id = int(self.player_id) if self.player_id is not None else 0
                # If not connected maybe board.ready is False
                if not getattr(board, 'ready', False):
                    # If game isn't started yet and we have no start, call start
                    board = self.send_move('start', '', 0)
                    time.sleep(loop_delay)
                    continue

                if getattr(board, 'currentTurn', 0) != my_id:
                    time.sleep(loop_delay)
                    continue

                # Find available moves
                moves = self.find_moves(board)
                choice = self.pick_move(moves, board)
                if choice is None:
                    time.sleep(loop_delay)
                    continue
                action, value, location, source = choice
                # Some moves like 'deal' set value to '', and location might be 0
                board = self.send_move(action, value, location, source=source)
                # Small delay to avoid flooding the server
                time.sleep(loop_delay)

        except KeyboardInterrupt:
            logger.info("Agent interrupted by user; exiting")


def main():
    parser = argparse.ArgumentParser(description='Agent that connects to Cards server and plays')
    parser.add_argument('--policy', default='greedy', choices=['greedy', 'random'], help='Policy for making moves')
    parser.add_argument('--delay', default=0.3, type=float, help='Loop delay (seconds) between board polls')
    args = parser.parse_args()

    agent = Agent(policy=args.policy)
    agent.play_loop(loop_delay=args.delay)


if __name__ == '__main__':
    main()
