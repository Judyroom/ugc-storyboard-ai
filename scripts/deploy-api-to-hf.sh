#!/usr/bin/env bash
# Deploys apps/api (as committed on the current HEAD) to the Hugging Face Space.
#
# Pushing to GitHub only redeploys the web app on Vercel; the API has to be pushed here.
# The Space repo keeps apps/api's files at its root, so this builds a commit on top of
# the Space's current main with those files and pushes it. Tests and scripts stay out.
#
# Usage (from the repo root, with the `hf` remote set up):  bash scripts/deploy-api-to-hf.sh [--yes]
# It lists the changes and asks before pushing, since a push restarts the live backend.
# First push asks for credentials: username = your HF username, password = an HF token
# with write access (https://huggingface.co/settings/tokens).

set -euo pipefail

REMOTE="${HF_REMOTE:-hf}"
SOURCE_REF="$(git rev-parse --short HEAD)"
WORKTREE="$(mktemp -d)"

cleanup() {
  git worktree remove --force "$WORKTREE" >/dev/null 2>&1 || true
}
trap cleanup EXIT

if [ -n "$(git status --porcelain -- apps/api)" ]; then
  echo "apps/api has uncommitted changes; commit them first so the Space matches a real commit." >&2
  exit 1
fi

git fetch "$REMOTE" main
git worktree add --detach "$WORKTREE" "$REMOTE/main" >/dev/null

# Replace everything except the Space's own git metadata and .gitattributes.
find "$WORKTREE" -mindepth 1 -maxdepth 1 ! -name .git ! -name .gitattributes -exec rm -rf {} +

git archive HEAD apps/api \
  ':(exclude)apps/api/tests' \
  ':(exclude)apps/api/scripts' \
  ':(exclude)apps/api/requirements-dev.txt' \
  | tar -x -C "$WORKTREE" --strip-components=2

printf '__pycache__/\n*.pyc\n.env\ngenerated/*\n!generated/.gitkeep\n' > "$WORKTREE/.gitignore"

cd "$WORKTREE"
git add -A
if git diff --cached --quiet; then
  echo "Space already matches apps/api at $SOURCE_REF; nothing to deploy."
  exit 0
fi

echo "Changes to deploy to the Space (from $SOURCE_REF):"
git status --short

# Pushing restarts the live backend, so confirm unless --yes was passed.
if [ "${1:-}" != "--yes" ]; then
  read -r -p "Push to $REMOTE and rebuild the Space? [y/N] " answer
  case "$answer" in
    y|Y|yes|YES) ;;
    *) echo "Cancelled; nothing pushed."; exit 1 ;;
  esac
fi

git commit -q -m "Deploy API from ugc-storyboard-ai $SOURCE_REF"
git push "$REMOTE" HEAD:main
echo "Pushed. The Space rebuilds in a few minutes: https://huggingface.co/spaces/heyjudy/ugc-storyboard-backend"
