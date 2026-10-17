# Hy plans for CaMeL, measured on AgentDojo

An experiment on the `camel-plan-language` branch. It asks whether writing an
agent's plan in Hy instead of Python changes anything measurable in a
CaMeL-style defence against prompt injection.

## Background

[CaMeL](https://arxiv.org/abs/2503.18813) (Google, Google DeepMind and ETH
Zurich) defends a tool-using agent against prompt injection by design. A
privileged model turns the user's request into a small program. A custom
interpreter runs that program and tracks where every value came from. Data
from tools, which is where injected instructions hide, is only ever read by a
quarantined model that cannot call tools. Before each tool call a security
policy checks the provenance of the arguments, for example that the
recipient of a money transfer did not come from an untrusted document.

The plan is written in a restricted subset of Python. The
[released code](https://github.com/google-research/camel-prompt-injection) is
evaluated on [AgentDojo](https://github.com/ethz-spylab/agentdojo), a
benchmark of 97 everyday tasks in four suites (workspace, travel, banking,
slack) with 35 attacker goals injected into the data the agent reads.

## The question

Hy is a Lisp that compiles to Python's syntax tree. A Hy plan can therefore
run on CaMeL's own interpreter, with CaMeL's own policies, unchanged. Only the
language the privileged model writes differs. That isolates one variable:

> With the same model, tools, interpreter and policies, do plans written in Hy
> do better or worse than plans written in Python?

## Conditions

| | Python plans (`camel`) | Hy plans (`hycamel`) |
|---|---|---|
| Privileged model | `claude -p`, same model | same |
| System prompt | CaMeL's own | CaMeL's own, with the language section replaced by a Hy guide |
| Front end | `ast.parse` | Hy reader, form allowlist, Hy compiler to Python AST |
| Interpreter, capabilities | CaMeL | CaMeL, unchanged |
| Quarantined model | `claude -p`, JSON prompting | same |
| Policies | CaMeL's banking policies | same |
| Procedure | record plans without policies, replay with policies (CaMeL's own procedure) | same |

Both conditions use the same replacement for CaMeL's quarantined model,
because the original needs an API's native structured output. The only model
access here is the `claude` CLI, so both models are called through
`claude -p` with a replaced system prompt and no tools.

The Hy front end reads the plan, rejects every Hy form that runs code at
compile time (`defmacro`, `eval-and-compile`, `require`, `import`, `py`, …) or
that CaMeL does not support, and compiles the rest. Hy keeps the plan's line
numbers in the compiled tree, so CaMeL's error messages point at the Hy line
the model wrote.

## Hypotheses, written before running

| | Hypothesis | Expected |
|---|---|---|
| H1 | Security is the same, because the interpreter and policies are the same | attack success with policies near 0 % in both |
| H2 | Utility is lower with Hy, because models have seen far less Hy than Python, and the field test in the article showed no gain from s-expressions | Hy 5 to 15 points lower |
| H3 | Hy plans need more attempts (syntax and compile errors) | more retries per task with Hy |
| H4 | Cost is similar or higher with Hy: longer system prompt, more retries | 1.0 to 1.3 times Python |
| H5 | The front end blocks every compile-time code execution form | all adversarial plans in the tests rejected |

If H2 holds, the answer to "does Hy help here" is no, and the experiment has
still produced a measured result. Something that would change that: Hy plans
reaching the same utility, which would make the uniform tree of a Lisp a
cheap base for checks before execution (the next step would then be a static
check of the whole plan before any tool runs, as in
[CaMeLoT](https://arxiv.org/abs/2609.18674)).

## Scope of the pilot

The banking suite of AgentDojo v1.2 (CaMeL's version): 16 user tasks without
attack, and 16 × 9 = 144 user task and injection task pairs with the
`important_instructions` attack. One model (Claude Haiku through the CLI).
The other suites follow only if the pilot gives a reason.

## Files

| File | Purpose |
|---|---|
| `hyplan.py` | Hy front end: form check, compile to Python AST, hook into CaMeL's interpreter, Hy system prompt |
| `claude_cli.py` | `claude -p` as CaMeL's privileged model and as the quarantined model |
| `run.py` | record, replay with policies, summarize |
| `test_hyplan.py` | tests of the front end, no model calls |
| `repair_test.py` | round two's repair test, readable against original error messages; prepared, not run |

## Running

Needs AgentDojo and the CaMeL code, which are not dependencies of HyML:

```bash
git clone https://github.com/google-research/camel-prompt-injection camel
python -m venv venv && venv/bin/pip install -e camel -e <path to hyml> pytest
venv/bin/python -m pytest experiments/camel_hy
venv/bin/python experiments/camel_hy/run.py record --condition python --suite banking
venv/bin/python experiments/camel_hy/run.py record --condition hy --suite banking
venv/bin/python experiments/camel_hy/run.py replay --condition python --suite banking
venv/bin/python experiments/camel_hy/run.py replay --condition hy --suite banking
venv/bin/python experiments/camel_hy/run.py summary
```

`record` makes real model calls. Add `--attack` for the attacked runs.
Results go to `experiments/camel_hy/runs/`, which is not committed.

## Results

Run on 12 October 2026 with Claude Haiku through `claude -p`, banking suite,
AgentDojo v1.2. The attacked runs were stopped early to save model calls, so
they cover 39 user task and injection task pairs that both conditions
finished, not all 144. These 39 come from the user tasks that finished first,
so they are not a random sample. Each condition crashed once in the
no-attack run, inside CaMeL's interpreter, and those two tasks were rerun.
Later crashes counted as failures.

Utility on exactly the same runs in both conditions:

| | Python plans | Hy plans |
|---|---:|---:|
| No attack, 16 tasks | 11 (69 %) | 10 (63 %) |
| No attack, with policies | 6 (38 %) | 6 (38 %) |
| Attacked, 39 pairs | 38 (97 %) | 32 (82 %) |
| Attacked, with policies | 11 (28 %) | 10 (26 %) |
| Attacks that succeeded, with or without policies | 0 | 0 |
| Retries per run, no attack / attacked | 1.25 / 0.62 | 1.56 / 1.10 |
| Output tokens per model call, no attack / attacked | 1,350 / 1,560 | 2,390 / 2,060 |
| Cost of the no-attack run | $0.74 | $1.08 |

Counted pair by pair over all 55 runs without policies, Python solved 8 that
Hy did not, and Hy solved 1 that Python did not (sign test, p ≈ 0.04).

### What the hypotheses came to

| | Hypothesis | Outcome |
|---|---|---|
| H1 | Same security | Held, but says little. No attack succeeded in either condition, even before the policies were applied, so the policies had nothing to stop in this sample. |
| H2 | Hy 5 to 15 points lower utility | Held. 6 points lower without attack, 15 points lower under attack, and 8 to 1 counted pair by pair. |
| H3 | More retries with Hy | Held. 1.25 against 1.56 retries per run without attack, 0.62 against 1.10 under attack. |
| H4 | Cost 1.0 to 1.3 times | Somewhat higher than expected. The no-attack run cost 1.46 times as much, and Hy replies were 1.3 to 1.8 times longer per call. |
| H5 | Front end blocks compile-time code | Held. All 17 forbidden-form cases in `test_hyplan.py` are rejected before anything compiles, and a macro body is never executed. |

### Where Hy plans failed

The extra errors with Hy came from the model carrying Python and Clojure
habits into Hy: `true` for `True`, `first`, `(str | None)` as a type,
`(print "=" * 50)` with infix `*`, and Python escaping inside Hy f-strings.
The error messages made some of these worse, because Hy reports a misplaced
operator by its mangled name (`name 'hyx_XasteriskX' is not defined`), which
the model never wrote. Showing the original name would be an easy improvement,
but it was not tested here.

### Conclusion

Writing the plan in Hy instead of Python made CaMeL's agent worse with this
model, with lower utility, more retries and higher cost, and no change in
security, which comes from the interpreter and the policies and not from the
language. This is the same result as the field test in the article, where
s-expressions gave the models no advantage. The Hy front end works and is
safe to compile, but there is no reason here to prefer it over Python.

Two side observations about CaMeL itself, from a small sample. With Haiku,
the `important_instructions` attack never succeeded even without policies,
because injected text only reaches the quarantined model, which cannot call
tools. And the banking policies cut utility roughly in half, mostly by
denying legitimate transfers whose recipient came from tool data.

## Round two: what closes the gap

The first round showed why Hy plans did worse. The model carried Python and
Clojure habits into Hy (`true`, `first`, infix `*`, `str | None`, Python
escaping in f-strings), and Hy reported some of these by mangled names such as
`hyx_XasteriskX` that the model never wrote. Round two tests two remedies,
each on its own, against the same Python and Hy baselines.

| Condition | Change |
|---|---|
| `hy-errors` | Error messages show the names as written, and an undefined operator, `true`, `first` and similar get a one-line hint, such as "`*` is a function in Hy, not an infix operator. Write (* a b)". The prompt is the round-one Hy prompt. |
| `hy-sheet` | The prompt adds a short list of these common mistakes. Errors are reported as in round one. |

Everything else is as in round one: the same model, interpreter, policies and
procedure. The question is whether the gap comes from the model not knowing
Hy, which a better prompt or better errors can fix, or from something they
cannot.

### Hypotheses, written before running

| | Hypothesis | Expected |
|---|---|---|
| H6 | Readable errors cut the retries that Hy plans needed | `hy-errors` retries per run at least a third below `hy` |
| H7 | The list of common mistakes prevents errors before they happen | `hy-sheet` retries per run at least a third below `hy` |
| H8 | Either remedy recovers most of the utility gap | `hy-errors` or `hy-sheet` within 5 points of Python |
| H9 | Security is unchanged | no attack succeeds in any condition |

### Procedure

A pilot of 10 banking tasks without attack per condition comes first, to
measure tokens and cost before the full run. The full run then covers all
16 tasks without attack and all 144 attacked pairs in every condition, so the
attacked sample is not limited to the tasks that finished first.

### Results

Run on 17 October 2026 with Claude Haiku through `claude -p`. Only the pilot
was run. The analysis below, made from round one's logs at no cost, showed
that the full run could not answer the question, so it was not made.

**The pilot**, user tasks 0 to 9 of the banking suite without attack, against
round one's runs of the same tasks:

| Condition | Utility | Retries | Output tokens | Cost |
|---|---:|---:|---:|---:|
| Python (`camel`) | 9 of 10 | 17 | 52,700 | $0.58 |
| Hy (`hycamel`) | 8 of 10 | 16 | 91,500 | $0.73 |
| Hy, readable errors (`hycamel-errors`) | 8 of 10 | 12 | 74,000 | $0.64 |
| Hy, list of common mistakes (`hycamel-sheet`) | 8 of 10 | 10 | 96,700 | $0.78 |

Errors caused by the language itself fell from about 9 in plain Hy to 5 with
readable errors and 6 with the list. Utility did not change, and without an
attack the gap to Python was one task, too small for the pilot to show
whether it closes. Each new condition had one task crash inside CaMeL's
interpreter on a class definition written in Hy (`TypeError: 'type' object
is not iterable`), as in round one, and the crash counts as a failure.

**What the Hy errors were.** Round one's Hy runs had 36 errors that come from
the language. The readable rewrite was then extended to cover 30 of them, and
round one's own logs show what the model did with the original messages.

| Error | Cases | Fixed on the next attempt with the original message |
|---|---:|---:|
| `if` without an else branch, a Clojure habit, reported as `parse error for pattern macro 'if': got unexpected end of macro call` | 10 | 10 |
| An undefined name: `first`, `true`, an infix `*` reported as `hyx_XasteriskX` | 9 | 9 |
| An unbalanced parenthesis | 3 | 3 |
| Python quoting inside a Hy f-string | 4 | 2 |
| `lfor` without the value to collect | 4 | 1 |

The model understood nearly every error at once, however cryptic its
message. A readable message could have helped in five cases at most, so a
test of readable against original messages, prepared in `repair_test.py`, was
not run.

**What cost Hy the tasks.** Python solved 8 of round one's runs that Hy did
not. None of the 8 Hy runs crashed or ran out of attempts. Each finished
with a wrong result. What these runs had in common was more retries.

| | Mean retries, solved runs | Mean retries, failed runs |
|---|---:|---:|
| Python | 0.81 | 0.50 |
| Hy | 1.02 | 2.00 |

In the 8 lost tasks Hy needed 0 to 4 retries, mostly 3 or 4, where Python
needed 0 to 4, mostly none. CaMeL continues each retry from a partly run plan,
so each extra round is another chance for the plan to go astray. With 8 tasks
this is a lead, not a result.

### What the hypotheses came to

| | Hypothesis | Outcome |
|---|---|---|
| H6 | Readable errors cut retries by a third | Pilot only, 16 to 12 retries in 10 tasks. The model fixed most errors at once without them, so there was little to cut. |
| H7 | The list of common mistakes cuts retries by a third | Pilot only, 16 to 10 retries in 10 tasks. |
| H8 | A remedy recovers most of the utility gap | Not tested. The pilot showed no change, and the gap rests on round one's small sample. |
| H9 | Security unchanged | Not tested, since no attacked runs were made. |

### Conclusion of round two

The gap between Hy and Python plans did not come from the model failing to
understand Hy's error messages. It fixed nearly all of them at the next
attempt. It came, as far as 8 tasks can show, from Hy plans needing more
attempts, each of which continues from a partly run plan. Avoiding the errors
matters more than explaining them, which points at the list of common
mistakes rather than at readable messages, but showing a gain in completed
tasks would take the full run and would likely find a small effect. The
experiment stops here, at $1.42 for the pilot. Both remedies stay in the
code as conditions (`hy-errors`, `hy-sheet`) for anyone who wants to run them
further.
