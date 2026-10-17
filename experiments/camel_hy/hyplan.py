"""Hy plans for CaMeL's interpreter.

A plan written in Hy is read, checked against an allowlist of Hy forms and
compiled to a Python syntax tree, which CaMeL's own interpreter then runs.
Nothing is evaluated by Hy itself. The check rejects every form that would run
code while compiling (macros, `eval-and-compile`, `require`, ...), so compiling
an untrusted plan is safe.
"""

import ast
import builtins
import os
import re
import types

import hy
import hy.models
from hy.compiler import hy_compile

from camel import system_prompt_generator as spg
from camel.interpreter import interpreter as ci
from camel.interpreter import result

# Hy's core forms and macros (mangled names), loaded by importing hy
HY_FORMS = frozenset(builtins._hy_macros)

# Forms a plan may use. Everything else in HY_FORMS is rejected. Operators
# (`+`, `=`, `.`, ...) are mangled to hyx_... names and all allowed.
ALLOWED_FORMS = frozenset({
    "and", "or", "not", "in", "not_in", "is", "is_not", "chainc", "bnot",
    "if", "when", "cond", "do", "else",
    "setv", "setx", "let", "annotate",
    "for", "lfor", "sfor", "dfor",
    "get", "cut",
    "defclass", "raise",
    "unpack_iterable", "unpack_mapping",
}) | {f for f in HY_FORMS if f.startswith("hyx_")}

FENCE = re.compile(r"```([a-zA-Z0-9_+\-#]*)\n")
HY_FENCES = {"hy", "hylang", "lisp", "clojure", "scheme"}


class PlanFormError(Exception):
    """A Hy form that plans may not use."""

    def __init__(self, message, model):
        super().__init__(message)
        self.lineno = getattr(model, "start_line", None) or 1
        self.end_lineno = getattr(model, "end_line", None) or self.lineno


def check_forms(models):
    """Raise PlanFormError for the first form outside ALLOWED_FORMS."""
    stack = list(models)
    while stack:
        m = stack.pop()
        if isinstance(m, hy.models.Expression) and m and isinstance(m[0], hy.models.Symbol):
            name = hy.mangle(m[0])
            if name in HY_FORMS and name not in ALLOWED_FORMS:
                raise PlanFormError(f"`{m[0]}` is not allowed in plans", m)
        # Expressions, lists, dicts, sets and f-strings are all Sequences
        if isinstance(m, hy.models.Sequence):
            stack.extend(m)


def compile_plan(source):
    """Hy source -> Python ast.Module, with the plan's own line numbers."""
    check_forms(list(hy.read_many(source, filename="<plan>")))
    module = types.ModuleType("camel_plan")
    tree = hy_compile(hy.read_many(source, filename="<plan>"), module, import_stdlib=False)
    # The compiler may add `import hy` for some values; plans can't import
    tree.body = [n for n in tree.body if not isinstance(n, ast.Import | ast.ImportFrom)]
    return tree


def is_hy(code):
    m = FENCE.search(code)
    return bool(m) and m.group(1).lower() in HY_FENCES


_parse_and_interpret_python = ci.parse_and_interpret_code


def parse_and_interpret_code(code, namespace, tool_calls_chain, dependencies, eval_args):
    """CaMeL's entry point, extended to Hy code blocks."""
    if not is_hy(code):
        return _parse_and_interpret_python(code, namespace, tool_calls_chain, dependencies, eval_args)
    try:
        source = ci.extract_code_block(code)
    except ci.InvalidOutputError as e:
        node = ast.expr(lineno=0, end_lineno=-1)
        return ci.EvalResult(result.Error(ci.CaMeLException(e, (node,), ())), namespace, tool_calls_chain, dependencies)
    try:
        tree = compile_plan(source)
    except (hy.errors.HyLanguageError, PlanFormError) as e:
        lineno = getattr(e, "lineno", None) or 1
        node = ast.expr(lineno=lineno, end_lineno=getattr(e, "end_lineno", None) or lineno)
        return _maybe_readable(ci.EvalResult(result.Error(ci.CaMeLException(e, (node,), ())), namespace, tool_calls_chain, dependencies))
    return _maybe_readable(ci.EvalResult(*ci.camel_eval(tree, namespace, tool_calls_chain, dependencies, eval_args)))


def _maybe_readable(eval_result):
    """Readable errors only in the conditions that ask for them (CAMEL_HY_ERRORS=1)."""
    if os.environ.get("CAMEL_HY_ERRORS") == "1":
        return readable_error(eval_result)
    return eval_result


# Readable errors (condition hy-errors). Hy reports a misplaced operator by its
# mangled name, `name 'hyx_XasteriskX' is not defined`, which the model never
# wrote. The message is rewritten with the names as written, and the habits
# from Python and Clojure seen in the first runs get a one-line hint.
MANGLED = re.compile(r"hyx_\w+")
OPERATORS = {"*", "+", "-", "/", "%", "**", "//", "=", "!=", "<", ">", "<=", ">=", "|", "&"}
HINTS = {
    "true": "Hy writes True, False and None as in Python; there is no true, false or nil.",
    "false": "Hy writes True, False and None as in Python; there is no true, false or nil.",
    "nil": "Hy writes True, False and None as in Python; there is no true, false or nil.",
    "null": "Hy writes True, False and None as in Python; there is no true, false or nil.",
    "first": "Hy has no first: write (get xs 0), and (get xs -1) for the last element.",
    "second": "Hy has no second: write (get xs 1).",
    "last": "Hy has no last: write (get xs -1).",
    "rest": "Hy has no rest: write (cut xs 1 None).",
    "nth": "Hy has no nth: write (get xs n).",
    "count": "Use (len xs) for the number of elements.",
}
UNDEFINED = re.compile(r"name '([^']+)' is not defined")


def _unmangle(m):
    try:
        return hy.unmangle(m.group())
    except Exception:  # not a name Hy made
        return m.group()


def readable_message(message):
    """An error message with Hy's mangled names unmangled and a hint for known habits."""
    text = MANGLED.sub(_unmangle, message)
    m = UNDEFINED.search(text)
    if m:
        name = m.group(1)
        if name in OPERATORS:
            text += (f"\nHint: `{name}` is a function in Hy, not an infix operator. "
                     f"Write ({name} a b), not a {name} b.")
        elif name in HINTS:
            text += "\nHint: " + HINTS[name]
    return text


def readable_error(eval_result):
    """The same result, with a readable error message when it is an error."""
    if not isinstance(eval_result.result, result.Error):
        return eval_result
    camel_exc = eval_result.result.error
    exc = camel_exc.exception
    new_text = readable_message(str(exc))
    if new_text == str(exc):
        return eval_result
    try:
        new_exc = type(exc)(new_text)
    except Exception:  # an exception type that wants other arguments
        new_exc = RuntimeError(f"{type(exc).__name__}: {new_text}")
    new_camel = ci.CaMeLException(new_exc, camel_exc.nodes, camel_exc.dependencies, camel_exc.metadata)
    return ci.EvalResult(result.Error(new_camel), eval_result.namespace, eval_result.tool_calls_chain,
                         eval_result.dependencies)


def install():
    """Route CaMeL's interpreter calls (live runs and replays) through this module."""
    ci.parse_and_interpret_code = parse_and_interpret_code


HY_LANGUAGE = """\
### Information on the language

Write the code in Hy, in one fenced code block marked ```hy. Hy is a Lisp \
that compiles to Python: the functions, types and methods listed above are \
the same, and only the syntax differs. A custom interpreter runs your code for \
security reasons.

How to write things in Hy:

- Call a function: `(get_balance)`. Keyword arguments: \
`(send_money :recipient iban :amount 10.0 :subject "Rent" :date "2022-04-01")`.
- Assign: `(setv total (sum amounts))`.
- Attributes and methods: `t.amount`, `(.join ", " names)`, `(.get d "key")`.
- Indexing: `(get xs 0)`, `(get d "key")`, nested `(get xs 0 "amount")`.
- Lists, dicts and sets: `[1 2 3]`, `{"a" 1 "b" 2}`, `#{1 2}`. Add an \
element without mutation: `[#* xs new_element]`.
- Comprehensions: `(lfor t txs :if (= t.sender "me") t.amount)`; `dfor` and \
`sfor` make dicts and sets.
- Conditionals: `(if test then else)`, `(when test body ...)`, \
`(cond test1 result1 test2 result2)`.
- Loops: `(for [t txs] (print t.subject))`.
- Operators are prefix: `(= a b)`, `(!= a b)`, `(> a b)`, `(+ a b)`, \
`(and a b)`, `(not a)`.
- f-strings work: `f"Total: {total}"`.
- Raise an error: `(raise (ValueError "No results"))`.
- A schema for `query_ai_assistant`: \
`(defclass Payment [BaseModel] #^ str iban #^ float amount)`, then \
`(query_ai_assistant "..." Payment)`.
- Write function and variable names exactly as listed, with underscores.

Follow these rules:

- Do not use `while`, `gfor` (generators), `break` or `continue`.
- You are not allowed to use `import`, `require`, `defmacro`, `eval-and-compile` or any other macro definition.
- You are absolutely not allowed to use `eval`, `exec`, `hy.eval` or `py`.
- Defining new functions with `defn` or `fn` is not supported.
- You are not allowed to use methods with side-effects (e.g., `.clear` or `.append`).
  Use instead functional alternatives such as comprehensions or the `[#* xs new_element]` syntax.
"""


# The cheat sheet (condition hy-sheet): the same habits, prevented up front
HY_PITFALLS = """
Common mistakes to avoid, habits from Python and Clojure that are wrong in Hy:

- Operators are always prefix, with no exceptions: `(* "=" 50)`, never `"=" * 50`; \
`(+ a b)`, never `a + b`.
- `True`, `False` and `None` are written as in Python. There is no `true`, `false` or `nil`.
- There is no `first`, `second`, `last`, `rest` or `nth`: use `(get xs 0)`, \
`(get xs -1)`, `(cut xs 1 None)` and `(get xs n)`.
- A union type such as `str | None` is written `(| str None)`.
- Do not nest quoted strings inside an f-string; build the string with `(+ ...)` \
or `(.format ...)` instead.
"""


def hy_sheet_system_prompt_generator(functions, classes_to_exclude=set()):
    """The Hy prompt with the common mistakes appended."""
    return hy_system_prompt_generator(functions, classes_to_exclude) + HY_PITFALLS


def hy_system_prompt_generator(functions, classes_to_exclude=set()):
    """CaMeL's system prompt, with its Python language section replaced by HY_LANGUAGE."""
    prompt = spg.default_system_prompt_generator(functions, classes_to_exclude)
    old_intro = "rewrites user requests to structured Python code."
    new_intro = "rewrites user requests to structured Hy code."
    assert old_intro in prompt
    prompt = prompt.replace(old_intro, new_intro)
    start = prompt.index("### Information on the language")
    return prompt[:start] + HY_LANGUAGE
