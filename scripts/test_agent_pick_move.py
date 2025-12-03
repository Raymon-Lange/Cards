#!/usr/bin/env python3
"""
Test pick_move prioritization: goal > hand > discard
"""
import sys
from os.path import abspath, dirname, join
sys.path.insert(0, abspath(join(dirname(__file__), '..')))

from Agent import Agent

agent = Agent.__new__(Agent)
agent.player_id = 0
agent.policy = 'greedy'

test_moves = [
    ('move', '9 of Clubs', '0', 'discard_1'),
    ('move', 'King of Hearts', '1', 'hand'),
    ('move', '5 of Diamonds', '2', 'goal'),
]

choice = Agent.pick_move(agent, test_moves, None)
print('Choice:', choice)
if choice[3] == 'goal':
    print('Success: picked goal move')
else:
    print('Failure: did not pick goal move')

random_moves = [('move', '2 of Clubs', '0', None), ('discard', '10 of Clubs', '3', 'hand')]
agent.policy = 'random'
choice2 = Agent.pick_move(agent, random_moves, None)
print('Random policy choice:', choice2)