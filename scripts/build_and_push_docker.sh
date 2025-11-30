#!/usr/bin/env bash

# Build and push Docker image tagged to the next 1.X version.
# It will detect the highest '1.N' tag (both local and remote) and increment N.
# Usage:
#   scripts/build_and_push_docker.sh [--image <image>] [--registry <registry>] [--push-latest] [--dry-run] [--yes] [--git-tag] [--force]
# Examples:
#   scripts/build_and_push_docker.sh --image raymonlange/cards-server --push-latest
#   scripts/build_and_push_docker.sh --dry-run
#
# By default, it builds the image using the Dockerfile in the repository root and tags it as <image>:1.X where X
# is the next minor/patch number in the 1 branch. It pushes the image to the registry (Docker Hub by default),
# and optionally tags and pushes 'latest'. It does NOT change git tags unless --git-tag is provided.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DEFAULT_IMAGE="raymonlange/cards-server"
IMAGE="$DEFAULT_IMAGE"
REGISTRY=""  # leave empty to tag image directly with image (Docker Hub example)
PUSH_LATEST=1
DRY_RUN=0
YES=0
GIT_TAG=0
FORCE=0

print_help() {
  cat <<'EOF'
Usage: build_and_push_docker.sh [options]
Options:
  --image IMAGE        Image name (default: raymonlange/cards-server)
  --registry REG       Registry host (e.g. myregistry.example.com). If provided the image will be tagged with this registry.
  --no-latest          Don't tag/push 'latest'
  --dry-run            Print everything the script would do but don't run build/push
  --yes                Don't prompt for confirmation
  --git-tag            Create and push a git tag for the new version
  --force              Force creating a tag even if the computed tag already exists
  -h, --help           Print help and exit
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --image)
      IMAGE="$2"; shift 2
      ;;
    --registry)
      REGISTRY="$2"; shift 2
      ;;
    --no-latest)
      PUSH_LATEST=0; shift
      ;;
    --dry-run)
      DRY_RUN=1; shift
      ;;
    --yes)
      YES=1; shift
      ;;
    --git-tag)
      GIT_TAG=1; shift
      ;;
    --force)
      FORCE=1; shift
      ;;
    -h|--help)
      print_help; exit 0
      ;;
    *)
      echo "Unknown option: $1"; print_help; exit 1
      ;;
  esac
done

# Helper: echo+exit on error
die() {
  echo "ERROR: $*" >&2
  exit 1
}

cd "$ROOT_DIR"

# Ensure repo present
if [[ ! -d .git ]]; then
  die "Not a git repository (no .git). This script expects to run at repo root."
fi

# Get tags (remote and local). We'll query origin for remote tags but fall back to local tags.
REMOTE_TAGS=""
if git rev-parse --verify origin >/dev/null 2>&1; then
  REMOTE_TAGS=$(git ls-remote --tags origin 2>/dev/null || true)
fi
LOCAL_TAGS=$(git tag --list 2>/dev/null || true)

# Collect tags that match v?1.N (no additional components; accepts v prefix)
collect_tags() {
  echo "$LOCAL_TAGS" | tr '\n' ' ' | sed 's/\s\+/\n/g' | grep -E '^v?1\.[0-9]+$' || true
  if [[ -n "$REMOTE_TAGS" ]]; then
    echo "$REMOTE_TAGS" | awk '{print $2}' | sed 's#refs/tags/##' | grep -E '^v?1\.[0-9]+$' || true
  fi
}

TAGS_LIST=$(collect_tags | tr '\n' ' ' | tr -s ' ' | sed 's/^ //;s/ $//')

# Normalize and extract number
max_n=-1
if [[ -n "$TAGS_LIST" ]]; then
  for t in $TAGS_LIST; do
    # Normalize to 1.N
    nt=$(echo "$t" | sed 's/^v//')
    if [[ "$nt" =~ ^1\.([0-9]+)$ ]]; then
      n=${BASH_REMATCH[1]}
      if (( n > max_n )); then
        max_n=$n
      fi
    fi
  done
fi

if (( max_n < 0 )); then
  # no existing 1.N tags, we'll start with 1.0
  new_n=0
else
  new_n=$((max_n + 1))
fi
new_tag="1.${new_n}"

if [[ -n "$REGISTRY" ]]; then
  image_name="${REGISTRY}/${IMAGE}:${new_tag}"
else
  image_name="${IMAGE}:${new_tag}"
fi

# Confirm behavior
cat <<EOF
Detected next tag: ${new_tag}
Image tag to build: ${image_name}
Push 'latest'?: ${PUSH_LATEST}
Dry run?: ${DRY_RUN}
Git tag?: ${GIT_TAG}
EOF

if [[ $DRY_RUN -eq 1 ]]; then
  echo "Dry run: exiting"
  exit 0
fi

if [[ $YES -ne 1 ]]; then
  echo -n "Proceed with building and pushing ${image_name}? [y/N]: "; read -r reply
  case "$reply" in
    y|Y) ;;
    *) echo "Aborting"; exit 1;;
  esac
fi

# Safety: Check if tag already exists in remote
exists_remote=0
if git rev-parse --verify origin >/dev/null 2>&1; then
  if git ls-remote --tags origin | grep -E "refs/tags/v?${new_tag}$" >/dev/null 2>&1; then
    exists_remote=1
  fi
fi

if [[ $exists_remote -eq 1 && $FORCE -ne 1 ]]; then
  echo "Remote tag ${new_tag} already exists. Use --force to continue anyway."
  exit 1
fi

# Build docker image
build_cmd=(docker build -t "${image_name}" .)
# Also create an intermediate image name without registry for local testing
if [[ -n "$REGISTRY" ]]; then
  # If registry is given, tag a local short name too
  short_tag="${IMAGE}:${new_tag}"
  build_cmd=(docker build -t "${short_tag}" -t "${image_name}" .)
fi

if [[ $DRY_RUN -eq 1 ]]; then
  echo "Would run: ${build_cmd[*]}"
else
  echo "Running: ${build_cmd[*]}"
  "${build_cmd[@]}"
fi

# Push it
if [[ $DRY_RUN -eq 1 ]]; then
  echo "Would push: docker push ${image_name}"
else
  echo "Pushing ${image_name}"
  docker push "${image_name}"
fi

# Optionally tag and push latest
if [[ $PUSH_LATEST -eq 1 ]]; then
  if [[ -n "$REGISTRY" ]]; then
    latest_image="${REGISTRY}/${IMAGE}:latest"
  else
    latest_image="${IMAGE}:latest"
  fi
  if [[ $DRY_RUN -eq 1 ]]; then
    echo "Would tag ${image_name} as ${latest_image} and push"
  else
    docker tag "${image_name}" "${latest_image}"
    docker push "${latest_image}"
  fi
fi

# Optionally create and push a git tag (without force by default)
if [[ $GIT_TAG -eq 1 ]]; then
  tag_name="v${new_tag}"
  if [[ $DRY_RUN -eq 1 ]]; then
    echo "Would create git tag: ${tag_name} and push"
  else
    if git rev-parse --verify "refs/tags/${tag_name}" >/dev/null 2>&1; then
      if [[ $FORCE -eq 1 ]]; then
        git tag -f "${tag_name}"
      else
        echo "Git tag ${tag_name} already exists; use --force to override"; exit 1
      fi
    else
      git tag "${tag_name}"
    fi
    git push origin "${tag_name}"
  fi
fi

echo "Done."
