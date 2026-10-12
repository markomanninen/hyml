#!/usr/bin/env bash
# Field test: agents make a product page whose review data carries a prompt
# injection, either by writing HTML themselves or through the hyml MCP server.
#
# Usage: run_agents.sh [REPEATS] [MODEL...]
#   REPEATS  runs per model and condition (default 3)
#   MODEL    claude | haiku (default: both)
#
# Needs: hyml-mcp on PATH (pip install 'hyml[mcp]') and the `claude` CLI.
# Every run makes real model calls.
set -euo pipefail

REPEATS="${1:-3}"
shift || true
if [ "$#" -gt 0 ]; then MODELS=("$@"); else MODELS=(claude haiku); fi
HERE="$(cd "$(dirname "$0")" && pwd)"
SERVER="$(command -v hyml-mcp)"
RUN="$HERE/runs/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$RUN"

for condition in html hyml-sexp hyml-json; do
  for model in "${MODELS[@]}"; do
    for n in $(seq "$REPEATS"); do
      dir="$RUN/$condition/$model-$n"
      mkdir -p "$dir"
      if [ "$condition" = html ]; then
        echo '{"mcpServers":{}}' > "$dir/mcp.json"
      else
        printf '{"mcpServers":{"hyml":{"type":"stdio","command":"%s","args":[],"env":{"HYML_OUTPUT_DIR":"%s"}}}}\n' \
          "$SERVER" "$dir" > "$dir/mcp.json"
      fi
      flags=()
      [ "$model" = haiku ] && flags=(--model haiku)
      (
        cd "$dir"
        # --tools "" leaves out Claude Code's built-in tools; only render_html is available
        timeout 600 claude -p "$(cat "$HERE/prompts/$condition.txt")" ${flags[@]+"${flags[@]}"} \
          --tools "" --strict-mcp-config --mcp-config mcp.json --allowedTools mcp__hyml \
          --output-format json > result.json 2> err.txt || true
      ) &
    done
  done
  wait
done

python3 "$HERE/field_test.py" "$RUN"
