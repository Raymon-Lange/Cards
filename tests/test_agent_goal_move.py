import sys
from os.path import abspath, dirname, join
import pytest

sys.path.insert(0, abspath(join(dirname(__file__), '..')))

from Agent import Agent
from Game import Board, Card


def make_agent_for_tests():
    agent = Agent.__new__(Agent)
    agent.player_id = 0
    agent.policy = 'greedy'
    agent.n = None
    return agent


def test_goal_top_ace_detected():
    board = Board(0)
    board.field = [[], [], [], []]
    board.playerOne.goal = [Card('Hearts', 'Ace')]
    agent = make_agent_for_tests()
    moves = Agent.find_moves(agent, board)
    assert any(m[3] == 'goal' for m in moves), "Goal top Ace should be detected as a move"


def test_goal_top_2_not_detected():
    board = Board(0)
    board.field = [[], [], [], []]
    board.playerOne.goal = [Card('Hearts', '2')]
    agent = make_agent_for_tests()
    moves = Agent.find_moves(agent, board)
    assert not any(m[3] == 'goal' for m in moves), "Goal top 2 should not be detected on empty field"


def test_discard_top_ace_detected():
    board = Board(0)
    board.field = [[], [], [], []]
    board.playerOne.discard[0].append(Card('Hearts', 'Ace'))
    agent = make_agent_for_tests()
    moves = Agent.find_moves(agent, board)
    assert any(m[3] and m[3].startswith('discard_') for m in moves), "Discard top Ace should be detected"


def test_hand_ace_detected_and_discard_option_added():
    board = Board(0)
    board.field = [[], [], [], []]
    board.playerOne.hand.append(Card('Hearts', 'Ace'))
    agent = make_agent_for_tests()
    moves = Agent.find_moves(agent, board)
    assert any(m[3] == 'hand' for m in moves), "Hand Ace should be detected as a move"
    # Ensure a discard option exists (fallback) if no field moves exist
    assert any(m[0] == 'discard' for m in moves), "Discard option expected in moves when hand is non-empty"
#!/usr/bin/env python3
"""
PyTest for Agent.find_moves: confirm goal pile top card is evaluated correctly.
"""
import sys
from os.path import abspath, dirname, join
sys.path.insert(0, abspath(join(dirname(__file__), '..')))

from Agent import Agent
from Game import Board, Card


def make_agent():
    agent = Agent.__new__(Agent)
    agent.player_id = 0
    agent.policy = 'greedy'
    agent.n = None
    return agent


def test_goal_top_ace_playable():
    board = Board(0)
    board.field = [[], [], [], []]
    board.playerOne.goal = [Card('Hearts', 'Ace')]
    agent = make_agent()
    moves = Agent.find_moves(agent, board)
    assert any(m[3] == 'goal' for m in moves), 'Goal top Ace should be playable'


def test_goal_top_2_not_playable():
    board = Board(0)
    board.field = [[], [], [], []]
    board.playerOne.goal = [Card('Hearts', '2')]
    agent = make_agent()
    moves = Agent.find_moves(agent, board)
    assert not any(m[3] == 'goal' for m in moves), 'Goal top 2 should not be playable on empty field'


def test_discard_top_ace_playable():
    board = Board(0)
    board.field = [[], [], [], []]
    board.playerOne.discard[0].append(Card('Hearts', 'Ace'))
    agent = make_agent()
    moves = Agent.find_moves(agent, board)
    assert any(m[3] and m[3].startswith('discard_') for m in moves), 'Discard top Ace should be playable'


def test_hand_ace_playable_and_discard_option():
    board = Board(0)
    board.field = [[], [], [], []]
    board.playerOne.hand.append(Card('Hearts', 'Ace'))
    agent = make_agent()
    moves = Agent.find_moves(agent, board)
    assert any(m[3] == 'hand' for m in moves), 'Hand Ace should be playable'
    assert any(m[0] == 'discard' for m in moves), 'Hand Ace should also include discard options'
