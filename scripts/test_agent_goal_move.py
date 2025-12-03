#!/usr/bin/env python3
"""
Simple test script for Agent.find_moves to confirm goal pile top card is evaluated correctly.
"""

import sys
from os.path import abspath, dirname, join
sys.path.insert(0, abspath(join(dirname(__file__), '..')))

from Agent import Agent
from Game import Board, Card

# Create a dummy board state
board = Board(0)
# Clear field
board.field = [[], [], [], []]
# Put a goal card for playerOne - make it an Ace so it can go onto empty field
board.playerOne.goal = [Card('Hearts', 'Ace')]
# Set player id so agent sees playerOne
agent = Agent.__new__(Agent)
agent.player_id = 0
agent.policy = 'greedy'
agent.n = None

# Run find_moves and print
def run_test_case(description, board, agent):
    moves = Agent.find_moves(agent, board)
    print('\nTest:', description)
    print('Moves returned:', moves)
    source_types = set(m[3] for m in moves)
    print('Sources present:', source_types)
    return moves

# Test 1: Goal top card playable (Ace on empty field)
moves = run_test_case('goal top Ace onto empty field', board, agent)
if any(m[3] == 'goal' for m in moves):
    print('Success: goal move detected')
else:
    print('Failure: goal move NOT detected')

# Test 2: Goal top card not playable (2 on empty field) => should not suggest goal moves
board2 = Board(0)
board2.field = [[], [], [], []]
board2.playerOne.goal = [Card('Hearts', '2')]
moves2 = run_test_case('goal top 2 onto empty field (not playable)', board2, agent)
if any(m[3] == 'goal' for m in moves2):
    print('Failure: goal move incorrectly detected')
else:
    print('Success: goal move correctly NOT detected')

# Test 3: Discard top card playable
board3 = Board(0)
board3.field = [[], [], [], []]
board3.playerOne.discard[0].append(Card('Hearts', 'Ace'))
moves3 = run_test_case('discard top Ace onto empty field', board3, agent)
if any(m[3] and m[3].startswith('discard_') for m in moves3):
    print('Success: discard top move detected')
else:
    print('Failure: discard top move NOT detected')

# Test 4: Hand card playable
board4 = Board(0)
board4.field = [[], [], [], []]
board4.playerOne.hand.append(Card('Hearts', 'Ace'))
moves4 = run_test_case('hand Ace onto empty field', board4, agent)
if any(m[3] == 'hand' for m in moves4):
    print('Success: hand move detected')
else:
    print('Failure: hand move NOT detected')
