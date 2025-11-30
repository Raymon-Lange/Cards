import socket
import logging
import os
from _thread import *
import threading
import pickle
from Game import *
import sys

# Configure logger to write to both server.log and stdout so Docker logs capture output
logger = logging.getLogger("GameServer")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Attempt to create a file handler using the LOG_PATH environment variable.
# If not set, default to a file named 'server.log' in the working directory.
raw_log_path = os.getenv('LOG_PATH', 'server.log')
logfile = os.path.expanduser(os.path.abspath(raw_log_path))
attempted_logfile = logfile
used_logfile = None

def _can_write_to_path(path: str) -> bool:
    """Return True if we can write to the provided path (create/append)."""
    try:
        dirname = os.path.dirname(path) or '.'
        if not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)
        # Open the file for append (this will create it if needed)
        with open(path, 'a') as f:
            f.write('')
        return True
    except Exception:
        return False

def _diagnose_path_issue(path: str) -> str:
    """Return a short diagnosis string to help users fix permission issues."""
    try:
        st = os.stat(path)
        owner_uid = st.st_uid
        owner_gid = st.st_gid
        return f"path exists, owned by uid={owner_uid}, gid={owner_gid}"
    except Exception:
        # Path not present, diagnose parent directory
        parent = os.path.dirname(path) or '.'
        try:
            st = os.stat(parent)
            return f"parent directory {parent} owned by uid={st.st_uid}, gid={st.st_gid}"
        except PermissionError as pe:
            return f"parent directory {parent} exists but cannot be stat-ed: {pe}"
        except FileNotFoundError:
            return f"parent directory {parent} does not exist"
        except Exception as e:
            return f"unable to determine owner or parent directory missing: {e}"

file_handler = None
if _can_write_to_path(logfile):
    try:
        file_handler = logging.FileHandler(logfile)
    except Exception as e:
        # Unexpected error while creating handler; fall back
        fallback_log = '/tmp/server.log'
        print(f"Warning: cannot open {logfile} for writing ({e}); falling back to {fallback_log}")
        if _can_write_to_path(fallback_log):
            try:
                file_handler = logging.FileHandler(fallback_log)
            except Exception:
                file_handler = None
        else:
            file_handler = None
else:
    fallback_log = '/tmp/server.log'
    diagnosis = _diagnose_path_issue(logfile)
    print(f"Warning: LOG_PATH '{logfile}' is not writable ({diagnosis}); falling back to {fallback_log}")
    if _can_write_to_path(fallback_log):
        try:
            file_handler = logging.FileHandler(fallback_log)
        except Exception:
            file_handler = None
    else:
        file_handler = None

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
if file_handler:
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# Record which logfile we are actually using for later user-facing messages
if file_handler:
    try:
        used_logfile = getattr(file_handler, 'baseFilename', None)
    except Exception:
        used_logfile = None
else:
    used_logfile = None

# Emit an informative message after handlers exist
if used_logfile and used_logfile != attempted_logfile:
    logger.warning(f"Could not use LOG_PATH '{attempted_logfile}', using '{used_logfile}' instead")
elif used_logfile:
    logger.info(f"Logging to '{used_logfile}'")
else:
    logger.warning("File logging disabled; logging to stdout only")

# NOTE: logger configured above

server = '0.0.0.0'
port = 5550

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Allow immediate reuse of the address after restart; prevents "address already in use" errors
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    s.bind((server, port))
except socket.error as e:
    logger.error(f"Socket binding error: {e}")
    sys.exit()

# Listen for incoming connections; missing listen() causes accept() to fail with EINVAL/Invalid argument
s.listen(5)
logger.info("Waiting for a connection, Server Started")

connected = set()
games = {}
idCount = 0
games_lock = threading.Lock()

def threaded_client(conn, p, gameId):
    global idCount
    conn.send(str.encode(str(p)))

    logger.info(f"Player {p} connected to game {gameId}")

    while True:
        try:
            data = conn.recv(4096).decode()

            if gameId in games:
                board = games[gameId]

                if not data:
                    break
                else:
                    if data == "reset":
                        board.reset()
                        logger.info(f"Game {gameId} reset by Player {p}")
                    elif data != "get":
                        board.play(data, p)
                        logger.info(f"Game {gameId}: Player {p} played {data}")

                    conn.sendall(pickle.dumps(board))
            else:
                break
        except Exception as error:
            logger.error(f"An error occurred: {error}")
            break

    logger.info("Lost connection")
    try:
        with games_lock:
            del games[gameId]
            logger.info(f"Closing Game {gameId}")
    except KeyError:
        pass
    conn.close()

try:
    while True:
        try:
            conn, addr = s.accept()
        except OSError as e:
            logger.error(f"Socket accept error: {e}")
            break
        logger.info(f"Connected to: {addr}")

        # Protect access to idCount and games so we don't race with other threads
        with games_lock:
            idCount += 1
            p = 0
            gameId = (idCount - 1) // 2
            if idCount % 2 == 1:
                games[gameId] = Board(gameId)
                logger.info(f"Creating a new game {gameId}")
            else:
                # If gameId isn't present (previous player disconnected), create a new Board
                if gameId not in games:
                    logger.warning(f"Game {gameId} not found when second player connected; creating a new game")
                    games[gameId] = Board(gameId)
                games[gameId].startGame()
                p = 1
                logger.info(f"Game {gameId} is now ready")

        start_new_thread(threaded_client, (conn, p, gameId))
except KeyboardInterrupt:
    logger.info("Shutting down server (KeyboardInterrupt)")
finally:
    try:
        s.close()
    except Exception:
        pass