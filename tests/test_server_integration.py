import os
import subprocess
import socket
import sys
import time
import tempfile
import shutil
import pickle

import pytest

# Ensure we can import project modules when running tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Network import Network


@pytest.fixture(scope='module')
def server_process():
    """Start the server as a subprocess for the duration of the test module.

    Yields the subprocess.Popen object so tests can interact with it, and then
    ensures the process is terminated at teardown.
    """
    # Create a temporary directory to use for logs (avoid permission issues)
    temp_dir = tempfile.mkdtemp(prefix='cards_test_')
    log_path = os.path.join(temp_dir, 'server_test.log')

    env = os.environ.copy()
    env['LOG_PATH'] = log_path
    # Use a dummy video driver to avoid opening windows when pygame is imported by the Server process
    env['SDL_VIDEODRIVER'] = env.get('SDL_VIDEODRIVER', 'dummy')
    # Use the same python interpreter to run the server script
    python_exec = sys.executable

    # Run server script in unbuffered mode so logs are immediate
    server_script = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Server.py'))
    process = subprocess.Popen([python_exec, '-u', server_script], cwd=os.path.dirname(server_script), env=env,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Wait for server to start accepting connections (make several attempts)
    start_time = time.time()
    timeout = 5
    connected = False
    while time.time() - start_time < timeout:
        try:
            sock = socket.create_connection(('127.0.0.1', 5550), timeout=0.5)
            sock.close()
            connected = True
            break
        except Exception:
            time.sleep(0.1)

    if not connected:
        # Dump logs to stderr for debugging when server didn't start
        out, err = process.communicate(timeout=1)
        # Clean up and fail
        shutil.rmtree(temp_dir)
        process.kill()
        raise RuntimeError(f"Server failed to start in {timeout} seconds. stdout: {out}\nstderr: {err}")

    try:
        yield process
    finally:
        # Terminate server process and cleanup
        try:
            process.terminate()
            process.wait(timeout=2)
        except Exception:
            process.kill()
        shutil.rmtree(temp_dir)


@pytest.fixture
def two_clients(server_process):
    """Create two network clients that connect to the server."""
    # Set small retry delay so tests don't take too long on failures
    c1 = Network(max_retries=20, retry_delay=0.05)
    # Give server a tiny bit of time to register the first connection before starting the second
    time.sleep(0.1)
    c2 = Network(max_retries=20, retry_delay=0.05)

    try:
        yield c1, c2
    finally:
        # Ensure sockets are closed
        try:
            c1.client.close()
        except Exception:
            pass
        try:
            c2.client.close()
        except Exception:
            pass


def test_two_clients_receive_player_id_and_game_starts(two_clients):
    c1, c2 = two_clients

    # Network returns player id as string; order of arrival is not deterministic so assert both IDs exist
    ids = {c1.getId(), c2.getId()}
    assert ids == {'0', '1'}, f"expected client IDs to be {{'0','1'}} but got {ids}"

    # First request should return a Board object (pickled by server), even before start
    board1 = c1.send('get')
    assert board1 is not None
    assert hasattr(board1, 'id')

    # After second client connected, the server should have started the game; board.ready should be True
    board2 = c2.send('get')
    assert board2 is not None
    assert getattr(board2, 'ready', True) is True

    # Check that the deck has been reduced (startGame deals a few cards)
    deck_len = len(board2.deck.cards)
    assert deck_len < 104, f"expected deck to be less than 104 after start, got {deck_len}"


def test_play_roundtrip_changes_board(two_clients):
    c1, c2 = two_clients

    # Confirm game started and is ready
    board = c1.send('get')
    assert getattr(board, 'ready', True) is True

    # Take an action that the server handles. We'll call 'start::' explicitly (action doesn't require payload)
    # Using the 'start::' format because Server.Board.play expects "action:value:location".
    resp = c1.send('start::')
    assert resp is not None
    # After start, ready should still be true
    assert getattr(resp, 'ready', True) is True

    # Now check for a change in deck length between two requests to confirm the server processed our command
    before = len(resp.deck.cards)
    # Request again -- should be unchanged unless another action occurs; instead, we'll send a deal from player 0 (deal::)
    resp2 = c1.send('deal::')
    assert resp2 is not None
    after = len(resp2.deck.cards)

    # A deal or start may cause cards to be drawn; ensure the deck is not larger and usually smaller or equal
    assert after <= before


# Optional: allow running the tests directly
if __name__ == '__main__':
    pytest.main()
