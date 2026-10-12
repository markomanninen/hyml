# Benchmarks and field test

These scripts produced the figures in [`doc/performance.md`](../doc/performance.md).

## Rendering speed

```
pip install -e . jinja2 htpy dominate
python benchmarks/render_bench.py
```

Renders a 33-element page and a 100-row table with the HyML macros,
`hyml.render`, `hyml.render_data`, Jinja2, htpy, dominate and f-strings. Before
timing, it checks that every implementation renders the same text. Figures are
the best of five runs in microseconds. The HyML macro versions are in
`pages.hy`.

## Security comparison

```
pip install -e . nh3 justhtml htpy
python benchmarks/security_compare.py
```

Gives ten attacks from agent output (scripts, event handlers, `javascript:`
URLs, image and CSS exfiltration, forms, links) to nh3, justhtml, htpy and HyML
data mode, and shows which ones pass through.

## Field test with real agents

```
pip install -e '.[mcp]' justhtml
benchmarks/field_test/run_agents.sh 3            # Claude and Haiku, three runs each
benchmarks/field_test/run_agents.sh 1 haiku      # a quick check
```

Claude Code agents (`claude -p` without built-in tools) make a product page
whose review data carries a prompt injection, in three conditions: writing the
HTML themselves, or rendering HyML s-expressions or JSON with the `hyml-mcp`
server. `field_test.py` summarizes tokens, cost, turns and whether the injection
reached the page. Runs are kept in `field_test/runs/` (not in git). Every run
makes real model calls; 18 runs cost about $0.80.
