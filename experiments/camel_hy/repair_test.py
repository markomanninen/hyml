"""Repair test: does a readable error message help the model fix its Hy plan?

Round one's logs hold every case where a Hy plan failed on an error. For each
case whose message the readable rewrite changes (see hyplan.readable_message),
this rebuilds the conversation the privileged model saw at that point, CaMeL's
Hy system prompt, the user's request and the earlier attempts with their
errors, and asks for the corrected plan twice: once with the original error
and once with the readable one. Nothing else differs.

The corrected plan is not run. It is checked statically:

  compiles   the plan passes Hy's reader and compiler and the form allowlist
  fixed      it compiles and no longer uses the undefined name it failed on

    python repair_test.py list             cases and the two messages, no model calls
    python repair_test.py run [--limit N]  real claude -p calls, results to runs/repair.jsonl
    python repair_test.py summary
"""

import argparse
import ast
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE / "runs"
sys.path.insert(0, str(HERE))

ERR = re.compile(r"^(\w+(?:Error|Exception|Input)): (.*)$", re.M)
UNDEFINED = re.compile(r"name '([^']+)' is not defined")


def text_of(message):
    return "".join(c.get("content") or "" for c in (message["content"] or []))


def cases():
    from hyplan import readable_message
    out = []
    for f in sorted((RUNS / "logs" / "claude-cli-haiku+hycamel" / "banking").glob("*/*/*.json")):
        msgs = json.loads(f.read_text())["messages"]
        for i, m in enumerate(msgs):
            if m["role"] != "user" or i == 0:
                continue
            text = text_of(m)
            if "Running the code gave the following error" not in text or not ERR.findall(text):
                continue
            readable = readable_message(text)
            if readable != text:
                etype, emsg = ERR.findall(text)[-1]
                name = UNDEFINED.search(emsg)
                out.append({"id": f"{f.parent.parent.name}/{f.parent.name}/{f.stem}#{i}", "file": str(f), "index": i,
                            "error": f"{etype}: {emsg}", "name": name.group(1) if name else None,
                            "raw": text, "readable": readable})
    return out


def system_prompt():
    from agentdojo.task_suite.load_suites import get_suite
    import hyplan
    suite = get_suite("v1.2", "banking")
    return hyplan.hy_system_prompt_generator(suite.tools)


def conversation(case, message):
    """The privileged model's view: the request, then each attempt and its error, the last error replaced."""
    msgs = json.loads(Path(case["file"]).read_text())["messages"]
    turns = [m for m in msgs[: case["index"]] if m["role"] in ("user", "assistant") and m["content"]]
    turns.append({"role": "user", "content": [{"type": "text", "content": message}]})
    return turns


def check(reply, case):
    """compiles, fixed: the corrected plan passes the Hy front end, and no longer uses the failing name."""
    import hyplan
    m = re.search(r"```(?:hy|hylang|lisp|clojure)?\n(.*?)```", reply, re.S)
    if not m:
        return False, False
    try:
        tree = hyplan.compile_plan(m.group(1))
    except Exception:
        return False, False
    if case["name"]:
        import hy
        bad = hy.mangle(case["name"]) if not case["name"].startswith("hyx_") else case["name"]
        names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
        return True, bad not in names
    return True, True


def run(limit):
    from claude_cli import call_claude, render_transcript
    os.environ["CAMEL_HY_USAGE"] = str(RUNS / "repair_usage.jsonl")
    system = system_prompt()
    out_path = RUNS / "repair.jsonl"
    done = {(r["id"], r["version"]) for r in map(json.loads, out_path.read_text().splitlines())} if out_path.exists() else set()
    for case in cases()[:limit]:
        for version in ("raw", "readable"):
            if (case["id"], version) in done:
                continue
            os.environ["CAMEL_HY_TASK"] = f"repair/{version}/{case['id']}/none"
            _, prompt = render_transcript([{"role": "system", "content": [{"type": "text", "content": system}]},
                                           *conversation(case, case[version])])
            reply = call_claude(system, prompt, "haiku", role="privileged")
            compiles, fixed = check(reply, case)
            row = {"id": case["id"], "version": version, "error": case["error"], "compiles": compiles,
                   "fixed": fixed, "reply_chars": len(reply)}
            with out_path.open("a") as f:
                f.write(json.dumps(row) + "\n")
            print(row["id"], version, "compiles" if compiles else "-", "fixed" if fixed else "-", flush=True)


def summary():
    rows = [json.loads(l) for l in (RUNS / "repair.jsonl").read_text().splitlines()]
    usage = [json.loads(l) for l in (RUNS / "repair_usage.jsonl").read_text().splitlines()] if (RUNS / "repair_usage.jsonl").exists() else []
    kinds = lambda e: ("if" if "'if'" in e else "lfor" if "'lfor'" in e else "name" if "is not defined" in e
                       else "f-string" if "f-string" in e or "string prefix" in e else "parenthesis")
    print(f"{'version':9} {'cases':>5} {'compiles':>9} {'fixed':>6}  by kind (fixed/cases)")
    for v in ("raw", "readable"):
        rs = [r for r in rows if r["version"] == v]
        by = {}
        for r in rs:
            k = kinds(r["error"]); a = by.setdefault(k, [0, 0]); a[0] += r["fixed"]; a[1] += 1
        print(f"{v:9} {len(rs):5} {sum(r['compiles'] for r in rs):9} {sum(r['fixed'] for r in rs):6}  "
              + ", ".join(f"{k} {a[0]}/{a[1]}" for k, a in sorted(by.items())))
        u = [x for x in usage if x["task"].startswith(f"repair/{v}/")]
        if u:
            print(f"{'':9} output tokens {sum(x['output_tokens'] for x in u)}, cost ${sum(x['cost_usd'] for x in u):.2f}")
    pairs = {}
    for r in rows:
        pairs.setdefault(r["id"], {})[r["version"]] = r["fixed"]
    both = [p for p in pairs.values() if len(p) == 2]
    print(f"pairs: readable fixed and raw not {sum(p['readable'] and not p['raw'] for p in both)}, "
          f"raw fixed and readable not {sum(p['raw'] and not p['readable'] for p in both)}, of {len(both)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["list", "run", "summary"])
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()
    if args.command == "list":
        cs = cases()
        for c in cs:
            print(c["id"], "|", c["error"][:100])
        print(len(cs), "cases;", len(system_prompt()), "characters of system prompt")
    elif args.command == "run":
        run(args.limit)
    else:
        summary()


if __name__ == "__main__":
    main()
