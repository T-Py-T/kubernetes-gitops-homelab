#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

./scripts/validate.sh

shellcheck .devcontainer/setup.sh scripts/ci-local.sh scripts/validate.sh

npm ci --ignore-scripts
export PATH="$repo_root/node_modules/.bin:$PATH"

markdownlint-cli2 "**/*.md" "#node_modules"
