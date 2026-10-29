#!/usr/bin/env bash
# Run the skill trigger evals with `claude plugin eval`.
# Builds a throwaway plugin from the skills that `links` installs into Claude Code,
# so each run sees the same skill set a real session does. Extra args pass through,
# e.g. `evals/run.sh --case 'teach-me*' --runs 1`.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

build=evals/.build/agent-config
rm -rf "$build"
mkdir -p "$build/.claude-plugin" "$build/skills"
printf '{ "name": "agent-config", "description": "Skills from dbanks12/agent-config, built for trigger evals" }\n' \
  > "$build/.claude-plugin/plugin.json"

# Same sources as ~/.claude/skills; a vendor submodule that is not cloned is skipped.
awk '$2 ~ /^~\/\.claude\/skills\// { print $1 }' links | while read -r src; do
  if [[ -f "$src/SKILL.md" ]]; then cp -RL "$src" "$build/skills/"; else echo "run.sh: skipped $src (not present)" >&2; fi
done
cp -R evals/triggers "$build/evals"

# --ablation none: a trigger test has no meaningful no-skill baseline, and one arm
# keeps the Skill graders scored.
timeout 5400 claude plugin eval "$build" --ablation none --trust-plugin --no-publish \
  --output-dir "evals/results/$(date -u +%Y-%m-%dT%H-%M-%SZ)" "$@"
