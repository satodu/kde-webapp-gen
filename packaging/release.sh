#!/bin/bash
# One-command release: bump version, test, tag, push, then publish to the AUR.
# Usage: packaging/release.sh 1.3.4
# The GitHub Actions workflow builds the AppImage and attaches it to the GitHub release on tag push.
set -euo pipefail

ROOT="$(cd "$(dirname "$(readlink -f "$0")")/.." && pwd)"
cd "$ROOT"

VERSION="${1:-}"
[[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || { echo "Usage: $0 MAJOR.MINOR.PATCH" >&2; exit 1; }

[ -z "$(git status --porcelain)" ] || { echo "ERROR: working tree not clean. Commit or stash first." >&2; exit 1; }
git rev-parse "$VERSION" >/dev/null 2>&1 && { echo "ERROR: tag $VERSION already exists." >&2; exit 1; }

echo "=== Running tests ==="
python3 -m pytest -q tests

echo "=== Bumping version to $VERSION ==="
sed -i "s/^APP_VERSION: str = \".*\"/APP_VERSION: str = \"$VERSION\"/" webapp_manager/constants.py
git add webapp_manager/constants.py
git commit -m "Release $VERSION"
git tag "$VERSION"
git push origin HEAD "$VERSION"

echo "=== Publishing to the AUR ==="
packaging/aur/publish.sh "$VERSION"

echo "=== Done. AppImage is being built by GitHub Actions: https://github.com/satodu/kde-webapp-gen/actions ==="
