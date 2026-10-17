"""Tests of the Hy front end. No model calls."""

import ast

import pytest
from agentdojo.task_suite.load_suites import get_suite
from agentdojo.functions_runtime import FunctionsRuntime
from camel.interpreter import interpreter as ci
from camel.interpreter import namespace as ns
from camel.interpreter import result
from camel.pipeline_elements.agentdojo_function import make_agentdojo_namespace
from camel.pipeline_elements.security_policies import BankingSecurityPolicyEngine
from camel.security_policy import NoSecurityPolicyEngine, SecurityPolicyDeniedError

import hyplan

hyplan.install()


def py(source):
    return ast.unparse(hyplan.compile_plan(source))


def test_plan_forms_compile_to_the_python_camel_expects():
    assert py("(setv txs (get_most_recent_transactions :n 100))") == "txs = get_most_recent_transactions(n=100)"
    assert py('(lfor t txs :if (= t.sender "me") t.amount)') == "[t.amount for t in txs if t.sender == 'me']"
    assert py('(.join ", " names)') == "', '.join(names)"
    assert py('(get xs 0 "amount")') == "xs[0]['amount']"
    assert py("(defclass P [BaseModel] #^ str iban #^ float amount)") == (
        "class P(BaseModel):\n    iban: str\n    amount: float"
    )
    assert py("[#* xs x]") == "[*xs, x]"


def test_line_numbers_are_the_plan_lines():
    tree = hyplan.compile_plan("(setv a 1)\n\n(setv b\n  (+ a 1))")
    assert [n.lineno for n in tree.body] == [1, 3]


@pytest.mark.parametrize(
    "source",
    [
        "(defmacro m [] (import os) (os.system \"echo pwned\"))",
        "(eval-and-compile (import os))",
        "(eval-when-compile (print 1))",
        "(require foo [bar])",
        "(import os)",
        '(py "__import__(\'os\')")',
        '(pys "x = 1")',
        "(do-mac (print 1))",
        "(defreader r 1)",
        "(defn f [] 1)",
        "(fn [] 1)",
        "(while True 1)",
        "(try 1 (except [e Exception] 2))",
        "(quasiquote (a (unquote b)))",
        # forbidden forms hidden in nested places
        "(setv x [1 (defmacro m [] 1)])",
        '(setv s f"{(eval-and-compile (import os))}")',
        '(setv d {"k" (require foo)})',
    ],
)
def test_forms_that_run_code_while_compiling_are_rejected(source):
    with pytest.raises(hyplan.PlanFormError):
        hyplan.compile_plan(source)


def test_unknown_reader_macros_are_rejected_by_the_reader():
    with pytest.raises(Exception, match="reader macro"):
        hyplan.compile_plan("#foo 1")


def test_macro_definition_is_never_executed(tmp_path):
    marker = tmp_path / "ran"
    with pytest.raises(hyplan.PlanFormError):
        hyplan.compile_plan(f'(defmacro m [] (.write-text (pathlib.Path "{marker}") "x") 1) (m)')
    assert not marker.exists()


def banking():
    suite = get_suite("v1.2", "banking")
    env = suite.load_and_inject_default_environment({})
    runtime = FunctionsRuntime(suite.tools)
    namespace = ns.Namespace.with_builtins()
    namespace = namespace.add_variables(make_agentdojo_namespace(namespace, runtime, env))
    return env, namespace


def run(code, policies=False):
    env, namespace = banking()
    engine = BankingSecurityPolicyEngine(env) if policies else NoSecurityPolicyEngine()
    eval_args = ci.EvalArgs(engine, ci.MetadataEvalMode.NORMAL)
    return ci.parse_and_interpret_code(code, namespace, [], (), eval_args)


def test_hy_plan_runs_on_camels_interpreter():
    res, namespace, calls, _ = run('```hy\n(setv b (get_balance))\n(print f"Balance: {b}")\n```')
    assert isinstance(res, result.Ok)
    assert [c.function for c in calls if c.function != "print"] == ["get_balance"]


def test_python_plans_still_go_to_the_python_parser():
    res, *_ = run("```python\nb = get_balance()\n```")
    assert isinstance(res, result.Ok)


def test_hy_errors_carry_the_plan_line():
    res, *_ = run("```hy\n(setv a 1)\n(setv b (+ a\n```")
    assert isinstance(res, result.Error)
    assert res.error.nodes[-1].lineno >= 2

    res, *_ = run("```hy\n(setv a 1)\n(defmacro m [] 1)\n```")
    assert isinstance(res, result.Error)
    assert isinstance(res.error.exception, hyplan.PlanFormError)
    assert res.error.nodes[-1].lineno == 2


def test_policies_apply_to_hy_plans():
    # The recipient comes from a file the attacker can write, so it is not trusted
    code = (
        "```hy\n"
        '(setv bill (read_file :file_path "bill-december-2023.txt"))\n'
        '(send_money :recipient bill :amount 10.0 :subject "x" :date "2022-01-01")\n'
        "```"
    )
    with pytest.raises(SecurityPolicyDeniedError):
        run(code, policies=True)
    res, *_ = run(code, policies=False)
    assert isinstance(res, result.Ok)


def test_system_prompt_differs_only_in_the_language_section():
    from camel import system_prompt_generator as spg

    suite = get_suite("v1.2", "banking")
    functions = FunctionsRuntime(suite.tools).functions.values()
    python_prompt = spg.default_system_prompt_generator(functions)
    hy_prompt = hyplan.hy_system_prompt_generator(functions)
    head = python_prompt[: python_prompt.index("### Information on the language")]
    assert hy_prompt.startswith(head.replace("structured Python code.", "structured Hy code."))
    assert "```hy" in hy_prompt


def test_readable_message_unmangles_and_hints():
    from hyplan import readable_message
    out = readable_message("name 'hyx_XasteriskX' is not defined")
    assert "name '*' is not defined" in out and "(* a b)" in out
    assert "There is no true" in readable_message("name 'true' is not defined")
    assert "(get xs 0)" in readable_message("name 'first' is not defined")
    # names Hy did not make are left as they are
    assert readable_message("name 'hyx_notreal' is not defined") == "name 'hyx_notreal' is not defined"
    assert readable_message("division by zero") == "division by zero"


def test_sheet_prompt_lists_the_pitfalls():
    from hyplan import HY_PITFALLS, hy_sheet_system_prompt_generator
    assert "(| str None)" in HY_PITFALLS and "True" in HY_PITFALLS
    assert callable(hy_sheet_system_prompt_generator)
