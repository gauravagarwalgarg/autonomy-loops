#!/usr/bin/env bash
# sync-remotes.sh Push to both GitHub and GitLab simultaneously.
#
# Usage:
#   ./scripts/sync-remotes.sh          # Push current branch to both
#   ./scripts/sync-remotes.sh --tags   # Push with tags
#
# Prerequisites:
#   git remote add github git@github.com:GauravAgarwalGarg/AutonomyLoops.git
#   git remote add gitlab git@gitlab.com:GauravAgarwalGarg/AutonomyLoops.git
#
# Or configure a single 'all' remote:
#   git remote add all git@github.com:GauravAgarwalGarg/AutonomyLoops.git
#   git remote set-url --add --push all git@github.com:GauravAgarwalGarg/AutonomyLoops.git
#   git remote set-url --add --push all git@gitlab.com:GauravAgarwalGarg/AutonomyLoops.git

set -euo pipefail

BRANCH=$(git rev-parse --abbrev-ref HEAD)
PUSH_ARGS="${*:---set-upstream}"

echo "╔══════════════════════════════════════════╗"
echo "║  AutonomyLoops Dual Platform Sync      ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "Branch: $BRANCH"
echo ""

# Check if 'all' remote exists (single push to both)
if git remote | grep -q '^all$'; then
    echo "→ Pushing to 'all' remote (GitHub + GitLab)..."
    git push all "$BRANCH" $PUSH_ARGS
    echo "✓ Done"
    exit 0
fi

# Otherwise push to each remote individually
FAILED=0

if git remote | grep -q '^github$'; then
    echo "→ Pushing to GitHub..."
    git push github "$BRANCH" $PUSH_ARGS && echo "  ✓ GitHub OK" || { echo "  ✗ GitHub FAILED"; FAILED=1; }
else
    echo "  ⚠ Remote 'github' not configured (skipping)"
fi

if git remote | grep -q '^gitlab$'; then
    echo "→ Pushing to GitLab..."
    git push gitlab "$BRANCH" $PUSH_ARGS && echo "  ✓ GitLab OK" || { echo "  ✗ GitLab FAILED"; FAILED=1; }
else
    echo "  ⚠ Remote 'gitlab' not configured (skipping)"
fi

# Fallback: push to 'origin' if neither explicit remote exists
if ! git remote | grep -qE '^(github|gitlab|all)$'; then
    echo "→ No github/gitlab/all remotes found. Pushing to 'origin'..."
    git push origin "$BRANCH" $PUSH_ARGS
fi

echo ""
if [ $FAILED -eq 0 ]; then
    echo "✓ All remotes synced"
else
    echo "✗ Some pushes failed (see above)"
    exit 1
fi
