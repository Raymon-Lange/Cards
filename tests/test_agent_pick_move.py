#!/usr/bin/env python3
"""
PyTest for Agent.pick_move prioritization: goal > hand > discard and random policy.
"""
import sys
from os.path import abspath, dirname, join
sys.path.insert(0, abspath(join(dirname(__file__), '..')))

from Agent import Agent


def make_agent():
    agent = Agent.__new__(Agent)
    agent.player_id = 0
    agent.policy = 'greedy'
    agent.n = None
    return agent


def test_pick_move_prioritizes_goal():
    agent = make_agent()
    test_moves = [
        ('move', '9 of Clubs', '0', 'discard_1'),
        ('move', 'King of Hearts', '1', 'hand'),
        ('move', '5 of Diamonds', '2', 'goal'),
    ]
    choice = Agent.pick_move(agent, test_moves, None)
    assert choice[3] == 'goal', 'pick_move should select a goal move when available'


def test_random_policy_works():
    agent = make_agent()
    agent.policy = 'random'
    random_moves = [('move', '2 of Clubs', '0', None), ('discard', '10 of Clubs', '3', 'hand')]
    choice = Agent.pick_move(agent, random_moves, None)
    assert choice in random_moves, 'random policy must return one of the provided moves'
