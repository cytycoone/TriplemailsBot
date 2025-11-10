#!/usr/bin/env bash
set -euo pipefail

# recover-and-push.sh
# Usage: run from the root of your project (where the broken .git lives)
# It will back up your repo, create a fresh git repo from the working tree,
# and force-push main to the origin remote detected in your broken repo.

TS=$(date +"%Y%m%d-%H%M%S")
WORKDIR="$(pwd)"
BACKUP_DIR="${WORKDIR}_backup_${TS}"
GIT_BROKEN_DIR="${WORKDIR}/.git_broken_${TS}"

echo "Working directory: ${WORKDIR}"
echo "Creating backup at: ${BACKUP_DIR}"
mkdir -p "${BACKUP_DIR}"

# 1) Backup everything (including .git)
echo "Backing up project files..."
cp -a "${WORKDIR}/." "${BACKUP_DIR}/"

# 2) Move broken .git out of the way (if present)
if [ -d ".git" ]; then
  echo "Moving broken .git to ${GIT_BROKEN_DIR}"
  mv .git "${GIT_BROKEN_DIR}"
else
  echo "No .git directory found in ${WORKDIR} – continuing with fresh repo init."
fi

# 3) Try to detect origin remote URL from the broken .git backup (if any)
REMOTE_URL=""
if [ -f "${GIT_BROKEN_DIR}/config" ]; then
  REMOTE_URL=$(sed -n "s/^[[:space:]]*url = //p" "${GIT_BROKEN_DIR}/config" | head -n1 || true)
fi

# fall back to any existing git remote config (in case .git survived)
if [ -z "${REMOTE_URL}" ]; then
  if git config --get remote.origin.url >/dev/null 2>&1; then
    REMOTE_URL=$(git config --get remote.origin.url)
  fi
fi

echo ""
if [ -n "${REMOTE_URL}" ]; then
  echo "Detected remote.origin.url = ${REMOTE_URL}"
else
  echo "No remote.origin.url detected."
  echo "If you want to push to GitHub, set REMOTE_URL below and re-run the script."
  echo "Example: REMOTE_URL=https://github.com/youruser/YourRepo.git ./recover-and-push.sh"
  echo ""
  read -p "Proceed without remote (local-only repo)? (y/N): " ans
  if [[ "${ans}" != "y" && "${ans}" != "Y" ]]; then
    echo "Aborting. Set REMOTE_URL or re-run when ready."
    exit 1
  fi
fi

# Allow override via environment variable
if [ -n "${REMOTE_URL:-}" ]; then
  : # keep detected
fi
if [ -n "${REMOTE_URL_OVERRIDE:-}" ]; then
  REMOTE_URL="${REMOTE_URL_OVERRIDE}"
  echo "REMOTE_URL overridden to: ${REMOTE_URL}"
fi

# 4) Initialize fresh git repo
echo "Initializing a fresh git repository..."
git init -q
git config user.name "recover-script"
git config user.email "recover@local"

# 5) Add everything and create a single commit
echo "Staging all files (excluding possible leftover .git_broken)..."
# ensure we don't stage the backup or broken .git we just created
git add -A
# If nothing to commit (edge case), still create an empty commit to have a branch head
if git rev-parse --verify HEAD >/dev/null 2>&1; then
  echo "Existing history detected in new repo (unexpected)."
else
  echo "Committing working tree..."
  git commit -m "Recreate repo from working tree (recovery ${TS})" || true
fi

# 6) Ensure branch is main
git branch -M main || true

# 7) Add remote if we have one and push
if [ -n "${REMOTE_URL}" ]; then
  echo "Adding origin -> ${REMOTE_URL}"
  git remote remove origin >/dev/null 2>&1 || true
  git remote add origin "${REMOTE_URL}"
  echo "Force-pushing 'main' to origin..."
  # Make the push show progress/errors to the user
  git push origin main --force --set-upstream
  echo ""
  echo "Force-push complete."
else
  echo "No remote configured. Local repo created. To push, run:"
  echo "  git remote add origin <your-remote-url>"
  echo "  git push -u origin main --force"
fi

echo ""
echo "Recovery complete."
echo "Backup of original workspace (including old .git) at: ${BACKUP_DIR}"
if [ -d "${GIT_BROKEN_DIR}" ]; then
  echo "Broken .git saved at: ${GIT_BROKEN_DIR}"
fi