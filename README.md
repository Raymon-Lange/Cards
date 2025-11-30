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
## Server

This project includes a TCP-based server implementation in `Server.py` which manages game sessions. Below are ways to run the server: locally for development, or inside Docker for a headless, reproducible deployment.

### Run the server locally (development)

1. Create and activate a virtual environment (optional but recommended):
```bash
python3 -m venv venv
source venv/bin/activate
```
2. Install the project dependencies:
```bash
pip install -r requirements.txt
```
3. For headless execution (no display), set the SDL video driver to dummy and start the server:
```bash
export SDL_VIDEODRIVER=dummy
python3 Server.py
```

This will start the server and bind to 0.0.0.0:5550 by default.

### Run the server in Docker (headless)

You can run `Server.py` inside a Docker container without a graphical display (the server doesn't need any UI). The repository includes a Dockerfile and Docker Compose configuration that will install dependencies and run the server.

Build the image:
```bash
docker build -t cards-server -f Dockerfile .
```

Run the container directly:
```bash
docker run -p 5550:5550 --name cards-server cards-server
```

Or use docker-compose:
```bash
docker compose up --build
```

The server listens on port `5550` by default; you can connect a client to <host-ip>:5550. If needed, you can remap the host port when running:
```bash
docker run -d -p 5551:5550 --name cards-server cards-server  # expose container port 5550 on host 5551
```

Notes:
- The image installs `pygame` as a dependency for the game logic. To keep the container headless we set `SDL_VIDEODRIVER=dummy` so pygame doesn't require a display.
- The server logs to `server.log` inside the container. Use `docker logs cards-server` to view console output (or `docker cp` to retrieve the file).
  - If you run the container with a non-root runtime user, the `Dockerfile` ensures the `/app` directory and `server.log` are owned by that runtime user so the server can write logs. If you still see permission errors when running the container, ensure any host volumes mounted into `/app` are writable by the container user or run the container as a user with proper access.
  - You can customize the logging path using the `LOG_PATH` environment variable. In Dockerfile and docker-compose the default is `/app/server.log`. To override, pass LOG_PATH on the `docker run` command or set it in `docker-compose.yml`.

    Example:
    ```bash
    docker run -e LOG_PATH=/tmp/cards-server.log -p 5550:5550 --name cards-server cards-server
    ```

  Logging behavior
  ----------------
  - The server will try to create and write to `LOG_PATH` on startup; if it cannot, it will diagnose the issue and **fallback to `/tmp/server.log`**. The server emits a warning message (printed to stdout and `docker logs`) when this occurs and logs the effective path. This helps debugging bind/permission issues when using host-mounted volumes or custom `LOG_PATH` values.

CLI helper script
-----------------
There's a helper script in `scripts/manage_server.sh` which provides a small CLI to build, start, stop, and view logs for the server container. It prints green on success and red on failure to help you quickly see status.

Examples:
```bash
# Build the image
Cards/scripts/manage_server.sh build

# Start the server (will build the image if missing)
Cards/scripts/manage_server.sh start

# Stop and remove the server container
Cards/scripts/manage_server.sh stop

# Check status
Cards/scripts/manage_server.sh status

# Follow logs
Cards/scripts/manage_server.sh logs
```

You can override default settings with flags:
- --name NAME for container name
- --image IMAGE for image name
- --port PORT for port mapping
- --dockerfile DOCKERFILE to supply a Dockerfile path

Security/notes:
- If you want to change the server listen port, edit `Server.py` and update the `port` value. Alternatively, you can map the internal port to a different host port using Docker run or docker compose port remapping.
- When running on production hosts, ensure the Docker daemon is managed and firewalls allow the chosen port.

## Running tests

This project uses `pytest` for integration tests. A new integration test has been added at `tests/test_server_integration.py` that starts the server as a subprocess and connects two clients to validate the socket protocol and game startup behavior.

To run the tests locally:

1. Create and activate a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate
```
2. Install dependencies (including pytest):
```bash
pip install -r requirements.txt
```
3. Run the test:
```bash
export SDL_VIDEODRIVER=dummy
python -m pytest -q tests/test_server_integration.py
```

Alternatively you can use the provided helper script to create a virtual environment and run the server integration tests:

```bash
scripts/run_server_tests.sh
```

Options:
- `--reuse-venv` - reuse `./venv` instead of recreating it
- `--no-install` - skip installing requirements

## Building and pushing Docker images

There's a helper script to build and push the Docker image for this project. It detects the next `1.X` version, builds the image, and pushes the new version tag (and optionally `latest`).

```bash
scripts/build_and_push_docker.sh --image raymonlange/cards-server --yes
```

Use `--dry-run` to preview the commands without making changes, and `--git-tag` to create a `v1.X` tag in git.

## Running an agent

You can run a built-in simple agent that connects to the server and plays moves automatically.

First, start the server locally:

```bash
export SDL_VIDEODRIVER=dummy
python3 Server.py
```

Then run the agent from the project root (optionally specifying a policy):

```bash
./venv/bin/python3 Agent.py --policy greedy --delay 0.3
```

The agent supports two simple policies:
- `greedy` (default): prefers moves that play to the field.
- `random`: selects a random legal move.

Tip: Start a human client (GUI) and an agent, then play against the agent.

The test will start a temporary server instance and connect two `Network` clients to ensure player IDs are assigned and that the game starts correctly. Ensure port `5550` is free before running the integration test.




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
