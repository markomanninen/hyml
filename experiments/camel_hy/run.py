"""Record, replay and summarize CaMeL runs with Python or Hy plans on AgentDojo.

    run.py record  --condition python|hy [--attack] [--suite banking] [--model haiku] [--user-tasks ...]
    run.py replay  --condition python|hy [--attack] ...
    run.py summary

`record` runs the privileged model live without policies, as CaMeL's own
main.py does, and makes real `claude -p` calls. `replay` re-runs the recorded
plans with the suite's security policies and makes no model calls.
"""

import argparse
import collections
import json
import os
import re
import sys
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE / "runs"
VERSION = "v1.2"
ATTACK = "important_instructions"


def pipeline_name(model, condition, replay=False):
    name = f"claude-cli-{model}+{'camel' if condition == 'python' else 'hycamel'}"
    return name + ("+secpol" if replay else "")


def build_pipeline(model, condition, suite_name, replay):
    from agentdojo import agent_pipeline
    from agentdojo.models import MODEL_NAMES
    from camel.pipeline_elements import privileged_llm
    from camel.pipeline_elements.replay_privileged_llm import PrivilegedLLMReplayer, UserInjectionTasksGetter
    from camel.pipeline_elements.security_policies import (
        ADNoSecurityPolicyEngine,
        BankingSecurityPolicyEngine,
        SlackSecurityPolicyEngine,
        TravelSecurityPolicyEngine,
        WorkspaceSecurityPolicyEngine,
    )

    import claude_cli
    import hyplan

    # The attack names the model in its injected text; pipeline names must contain a key
    MODEL_NAMES[f"claude-cli-{model}"] = "Claude"
    hyplan.install()
    claude_cli.install(model)
    if replay:
        engines = {
            "banking": BankingSecurityPolicyEngine,
            "slack": SlackSecurityPolicyEngine,
            "travel": TravelSecurityPolicyEngine,
            "workspace": WorkspaceSecurityPolicyEngine,
        }
        elements = [
            agent_pipeline.InitQuery(),
            UserInjectionTasksGetter(),
            PrivilegedLLMReplayer(pipeline_name(model, condition), ATTACK, engines[suite_name]),
        ]
    else:
        prompt = hyplan.hy_system_prompt_generator if condition == "hy" else None
        kwargs = {"system_prompt_generator": prompt} if prompt else {}
        elements = [
            agent_pipeline.InitQuery(),
            privileged_llm.PrivilegedLLM(
                claude_cli.ClaudeCLILLM(model), ADNoSecurityPolicyEngine, f"claude-cli:{model}", **kwargs
            ),
        ]
    pipeline = agent_pipeline.AgentPipeline(elements)
    pipeline.name = pipeline_name(model, condition, replay)
    return pipeline


def run_user_task(model, condition, suite_name, user_task, attack, replay, injection_tasks=None):
    """One user task (with all its injection tasks when attacked), in its own process."""
    sys.path.insert(0, str(HERE))
    os.chdir(RUNS)  # CaMeL's replay reads ./logs
    os.environ["CAMEL_HY_USAGE"] = str(RUNS / "usage.jsonl")
    os.environ["CAMEL_HY_TASK"] = f"{pipeline_name(model, condition, replay)}/{suite_name}/{user_task}/{ATTACK if attack else 'none'}"

    from agentdojo import attacks, benchmark
    from agentdojo.logging import OutputLogger
    from agentdojo.task_suite.load_suites import get_suite

    suite = get_suite(VERSION, suite_name)
    pipeline = build_pipeline(model, condition, suite_name, replay)
    logdir = Path("logs")
    with OutputLogger(str(logdir)):
        if attack:
            attack_obj = attacks.load_attack(ATTACK, suite, pipeline)
            if injection_tasks is None:
                res = benchmark.benchmark_suite_with_injections(
                    pipeline, suite, attack_obj, logdir, force_rerun=False, user_tasks=[user_task],
                    verbose=False, benchmark_version=VERSION,
                )
            else:
                utility, _security = benchmark.run_task_with_injection_tasks(
                    suite, pipeline, suite.get_user_task_by_id(user_task), attack_obj, logdir,
                    force_rerun=False, injection_tasks=injection_tasks, benchmark_version=VERSION,
                )
                res = {"utility_results": utility}
        else:
            res = benchmark.benchmark_suite_without_injections(
                pipeline, suite, logdir, force_rerun=False, user_tasks=[user_task], benchmark_version=VERSION
            )
    return user_task, {str(k): v for k, v in res["utility_results"].items()}


def run(args, replay):
    sys.path.insert(0, str(HERE))
    from agentdojo.task_suite.load_suites import get_suite

    RUNS.mkdir(exist_ok=True)
    suite = get_suite(VERSION, args.suite)
    user_tasks = args.user_tasks or sorted(suite.user_tasks, key=lambda t: int(t.split("_")[-1]))
    pairs = {ut: None for ut in user_tasks}
    if replay and args.attack:
        # Replay only pairs that both conditions recorded completely, so they are compared on the same set
        pairs = {ut: sorted(recorded_pairs(args.model, args.suite, ut)) for ut in user_tasks}
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [
            pool.submit(run_user_task, args.model, args.condition, args.suite, ut, args.attack, replay, its)
            for ut, its in pairs.items() if its != []
        ]
        for f in as_completed(futures):
            try:
                ut, utility = f.result()
                print(ut, sum(utility.values()), "/", len(utility), flush=True)
            except Exception as e:  # keep the other tasks running
                print("FAILED", "".join(traceback.format_exception(e))[-3000:], flush=True)


def recorded_pairs(model, suite_name, user_task):
    """Injection tasks recorded with results in both conditions."""
    found = []
    for condition in ("python", "hy"):
        d = RUNS / "logs" / pipeline_name(model, condition) / suite_name / user_task / ATTACK
        found.append({f.stem for f in d.glob("*.json") if "utility" in json.loads(f.read_text())})
    return found[0] & found[1]


ERROR_LINE = re.compile(r"^(\w+(?:Error|Exception|Input)): ", re.MULTILINE)


def summary(_args):
    rows = collections.defaultdict(lambda: collections.Counter())
    error_types = collections.defaultdict(collections.Counter)
    for path in (RUNS / "logs").glob("*/*/*/*/*.json"):
        name, suite, _ut, attack, _it = path.relative_to(RUNS / "logs").with_suffix("").parts
        data = json.loads(path.read_text())
        key = (name, suite, attack)
        r = rows[key]
        r["n"] += 1
        # A task that raised inside CaMeL's interpreter leaves a log without results
        r["utility"] += bool(data.get("utility"))
        r["attack_succeeded"] += bool(data.get("security"))
        r["crashed"] += "utility" not in data or data.get("error") is not None
        retries = 0
        for m in data["messages"]:
            if m["role"] == "user" and m["content"]:
                text = "".join(c.get("content") or "" for c in m["content"])
                if "Running the code gave the following error" in text:
                    retries += 1
                    error_types[key].update(ERROR_LINE.findall(text)[-1:])
                if text.startswith("SecurityPolicyDeniedError"):
                    r["denied"] += 1
        r["retries"] += retries
    usage = collections.defaultdict(collections.Counter)
    usage_path = RUNS / "usage.jsonl"
    if usage_path.exists():
        for line in usage_path.read_text().splitlines():
            u = json.loads(line)
            name, suite, _ut, attack = u["task"].split("/")
            c = usage[(name, suite, attack)]
            c[f"{u['role']}_calls"] += 1
            for k in ("input_tokens", "output_tokens", "cost_usd", "seconds"):
                c[k] += u[k]
    print(f"{'pipeline':38} {'suite':9} {'attack':22} {'n':>4} {'utility':>8} {'ASR':>6} {'denied':>6} {'crashed':>7} "
          f"{'retries':>8} {'P calls':>7} {'Q calls':>7} {'in tok':>9} {'out tok':>8} {'$':>7}")
    for key in sorted(rows):
        r, u = rows[key], usage.get(key, collections.Counter())
        n = r["n"]
        print(f"{key[0]:38} {key[1]:9} {key[2]:22} {n:4} {r['utility'] / n:8.1%} {(format(r['attack_succeeded'] / n, '6.1%') if key[2] != 'none' else '     -')} "
              f"{r['denied']:6} {r['crashed']:7} {r['retries'] / n:8.2f} {u['privileged_calls']:7} {u['quarantined_calls']:7} "
              f"{u['input_tokens']:9} {u['output_tokens']:8} {u['cost_usd']:7.2f}")
    for key in sorted(error_types):
        print(key[0], key[2], dict(error_types[key].most_common(8)))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("record", "replay"):
        p = sub.add_parser(command)
        p.add_argument("--condition", choices=["python", "hy"], required=True)
        p.add_argument("--suite", default="banking")
        p.add_argument("--model", default="haiku")
        p.add_argument("--attack", action="store_true")
        p.add_argument("--user-tasks", nargs="*")
        p.add_argument("--workers", type=int, default=6)
    sub.add_parser("summary")
    args = parser.parse_args()
    if args.command == "summary":
        summary(args)
    else:
        run(args, replay=args.command == "replay")


if __name__ == "__main__":
    main()
