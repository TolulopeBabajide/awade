#!/usr/bin/env sh
# AWD-M-03 — One-time setup for husky pre-commit hooks.
# Run from the repo root after `cd apps/frontend && npm install`.
#
# Usage:
#   cd <repo-root>
#   sh scripts/setup-hooks.sh

set -e

echo "Creating .husky/ directory..."
mkdir -p .husky

echo "Writing .husky/pre-commit..."
cat > .husky/pre-commit << 'HOOK'
#!/usr/bin/env sh
# Pre-commit: lint staged TypeScript files + full type check
cd apps/frontend && npx lint-staged && npx tsc --noEmit
HOOK

chmod +x .husky/pre-commit

echo "Done. Verify with: cat .husky/pre-commit"
echo "Then commit: git add apps/frontend/package.json apps/frontend/package-lock.json .husky/pre-commit scripts/setup-hooks.sh"
