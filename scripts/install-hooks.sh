#!/usr/bin/env bash
# install-hooks.sh — point git at the .husky/ hooks directory.
# Run once after cloning: bash scripts/install-hooks.sh
set -euo pipefail

git config core.hooksPath .husky
chmod +x .husky/pre-commit
echo "Git hooks installed — .husky/pre-commit is active."
