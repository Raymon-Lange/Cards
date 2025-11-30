#!/usr/bin/env bash
# CLI to manage the Docker server container for Cards
# Usage: manage_server.sh start|stop|status|build|restart|logs [--name NAME] [--image IMAGE] [--port PORT]

set -uo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
RESET='\033[0m'

CONTAINER_NAME="cards-server"
IMAGE_NAME="cards-server"
DOCKERFILE="Dockerfile"
PORT="5550"
LOG_PATH="/app/server.log"

print_help() {
  cat <<EOF
Usage: $0 <command> [options]

Commands:
  start        Build image (if missing) and run the server container in detached mode
  stop         Stop and remove the server container
  status       Print container status (running/stopped/not found)
  build        Build the Docker image
  restart      Restart the container (build -> stop -> start)
  logs         Follow the container logs
  help         Print this help

Options:
  --name NAME  Override the container name (default cards-server)
  --image IMG  Override the image name (default cards-server)
  --port PORT  Override the host -> container port (default 5550)
  --log-path PATH  Override the LOG_PATH environment variable passed to the container (default /app/server.log)
  --dockerfile DOCKERFILE  Path to Dockerfile (default Dockerfile)

EOF
}

color_echo() { # color_echo color message
  local colour="$1"; shift
  echo -e "${colour}$*${RESET}"
}

check_docker() {
  if ! docker info >/dev/null 2>&1; then
    color_echo "${RED}" "Docker is not available or daemon not running. Please start Docker and try again."
    return 1
  fi
  return 0
}

build_image() {
  check_docker || return 1
  color_echo "${YELLOW}" "Building Docker image ${IMAGE_NAME} from ${DOCKERFILE}..."
  if docker build -t "${IMAGE_NAME}" -f "${DOCKERFILE}" .; then
    color_echo "${GREEN}" "Image ${IMAGE_NAME} built successfully"
    return 0
  else
    color_echo "${RED}" "Docker build failed"
    return 1
  fi
}

container_exists() {
  docker ps -a --format '{{.Names}}' | grep -xq "${CONTAINER_NAME}"
}

container_running() {
  docker ps --format '{{.Names}}' | grep -xq "${CONTAINER_NAME}"
}

start_container() {
  check_docker || return 1

  # If image doesn't exist, build
  if ! docker image inspect "${IMAGE_NAME}" >/dev/null 2>&1; then
    if ! build_image; then
      return 1
    fi
  fi

  if container_running; then
    color_echo "${GREEN}" "Container ${CONTAINER_NAME} is already running"
    return 0
  fi

  if container_exists; then
    color_echo "${YELLOW}" "Starting existing container ${CONTAINER_NAME}..."
    if docker start "${CONTAINER_NAME}" >/dev/null; then
      color_echo "${GREEN}" "Container ${CONTAINER_NAME} started"
      return 0
    else
      color_echo "${RED}" "Failed to start container ${CONTAINER_NAME}"
      return 1
    fi
  fi

  color_echo "${YELLOW}" "Running new container ${CONTAINER_NAME} using image ${IMAGE_NAME}..."
  if docker run -d --name "${CONTAINER_NAME}" -e LOG_PATH="${LOG_PATH}" -p "${PORT}:${PORT}" "${IMAGE_NAME}" >/dev/null; then
    color_echo "${GREEN}" "Container ${CONTAINER_NAME} started and listening on port ${PORT}"
    return 0
  else
    color_echo "${RED}" "Failed to run container ${CONTAINER_NAME}"
    return 1
  fi
}

stop_container() {
  check_docker || return 1
  if ! container_exists; then
    color_echo "${YELLOW}" "Container ${CONTAINER_NAME} does not exist, nothing to stop"
    return 0
  fi

  if container_running; then
    color_echo "${YELLOW}" "Stopping container ${CONTAINER_NAME}..."
    if docker stop "${CONTAINER_NAME}" >/dev/null; then
      color_echo "${GREEN}" "Container ${CONTAINER_NAME} stopped"
    else
      color_echo "${RED}" "Failed to stop ${CONTAINER_NAME}"
      return 1
    fi
  else
    color_echo "${YELLOW}" "Container ${CONTAINER_NAME} is not running"
  fi

  # Remove container if it exists
  color_echo "${YELLOW}" "Removing container ${CONTAINER_NAME}..."
  if docker rm "${CONTAINER_NAME}" >/dev/null; then
    color_echo "${GREEN}" "Removed container ${CONTAINER_NAME}"
    return 0
  else
    color_echo "${RED}" "Failed to remove container ${CONTAINER_NAME}"
    return 1
  fi
}

status_container() {
  check_docker || return 1
  if container_running; then
    color_echo "${GREEN}" "Container ${CONTAINER_NAME} is running"
    docker ps --filter "name=${CONTAINER_NAME}" --format "{{.ID}} {{.Names}} {{.Status}} {{.Ports}}"
    return 0
  fi
  if container_exists; then
    color_echo "${YELLOW}" "Container ${CONTAINER_NAME} exists but is stopped"
    docker ps -a --filter "name=${CONTAINER_NAME}" --format "{{.ID}} {{.Names}} {{.Status}} {{.Ports}}"
    return 0
  fi
  color_echo "${RED}" "Container ${CONTAINER_NAME} not found"
  return 2
}

follow_logs() {
  check_docker || return 1
  if ! container_exists; then
    color_echo "${RED}" "Container ${CONTAINER_NAME} does not exist. Run start first."
    return 1
  fi
  docker logs -f "${CONTAINER_NAME}"
}

restart_container() {
  check_docker || return 1
  build_image || return 1
  stop_container || true
  start_container
}

# CLI parsing
if [[ $# -lt 1 ]]; then
  print_help
  exit 1
fi

POSITIONAL=()
COMMAND=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    start|stop|status|build|restart|logs|help)
      COMMAND="$1"; shift; break
      ;;
    --name)
      CONTAINER_NAME="$2"; shift 2
      ;;
    --image)
      IMAGE_NAME="$2"; shift 2
      ;;
    --port)
      PORT="$2"; shift 2
      ;;
    --log-path)
      LOG_PATH="$2"; shift 2
      ;;
    --dockerfile)
      DOCKERFILE="$2"; shift 2
      ;;
    --)
      shift; break
      ;;
    -*|--*)
      echo "Unknown option $1"
      print_help
      exit 1
      ;;
    *)
      POSITIONAL+=('$1'); shift
      ;;
  esac
done

case "$COMMAND" in
  start)
    start_container
    ;;
  stop)
    stop_container
    ;;
  status)
    status_container
    ;;
  build)
    build_image
    ;;
  restart)
    restart_container
    ;;
  logs)
    follow_logs
    ;;
  help|*)
    print_help
    ;;
esac

exit 0
