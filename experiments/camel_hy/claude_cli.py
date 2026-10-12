"""`claude -p` as CaMeL's privileged and quarantined models.

There are no API keys here, only the Claude Code CLI. Each call replaces the
CLI's system prompt, turns off all tools and MCP servers, and loads no user
settings, so the model sees the experiment's prompts and nothing else apart
from the CLI's short environment preamble, which is the same in every call.

Every call is appended to the JSONL file named by CAMEL_HY_USAGE, with its
role, tokens, cost and duration.
"""

import json
import os
import re
import subprocess
import tempfile
import time

from agentdojo import types as ad_types
from agentdojo.agent_pipeline import BasePipelineElement
from agentdojo.functions_runtime import EmptyEnv
from pydantic import BaseModel, Field, ValidationError, create_model
import pydantic_ai

from camel import quarantined_llm

EMPTY_DIR = tempfile.mkdtemp(prefix="camel-hy-cli-")


class ClaudeCLIError(Exception):
    pass


def call_claude(system, prompt, model, role, attempts=4, timeout=600):
    """One `claude -p` call. Returns the reply text."""
    cmd = [
        "claude", "-p", "--model", model,
        "--tools", "", "--strict-mcp-config", "--setting-sources", "",
        "--no-session-persistence", "--system-prompt", system,
        "--output-format", "json",
    ]
    for attempt in range(attempts):
        start = time.time()
        try:
            proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, cwd=EMPTY_DIR, timeout=timeout)
            data = json.loads(proc.stdout)
        except (subprocess.TimeoutExpired, json.JSONDecodeError) as e:
            data, error = None, repr(e)[:300]
        else:
            error = data.get("result") if data.get("is_error") else None
        if data is not None and error is None:
            _log_usage(role, model, data, time.time() - start)
            return data["result"]
        time.sleep(10 * (attempt + 1))
    raise ClaudeCLIError(f"claude -p failed {attempts} times: {error}")


def _log_usage(role, model, data, seconds):
    path = os.environ.get("CAMEL_HY_USAGE")
    if not path:
        return
    usage = data.get("usage", {})
    row = {
        "role": role,
        "model": model,
        "task": os.environ.get("CAMEL_HY_TASK", ""),
        "input_tokens": usage.get("input_tokens", 0) + usage.get("cache_read_input_tokens", 0)
        + usage.get("cache_creation_input_tokens", 0),
        "output_tokens": usage.get("output_tokens", 0),
        "cost_usd": data.get("total_cost_usd", 0),
        "seconds": round(seconds, 2),
    }
    with open(path, "a") as f:
        f.write(json.dumps(row) + "\n")


def render_transcript(messages):
    """System text and a single prompt from AgentDojo chat messages."""
    system = "\n\n".join(ad_types.get_text_content_as_str(m["content"]) for m in messages if m["role"] == "system")
    turns = [m for m in messages if m["role"] in ("user", "assistant") and m["content"]]
    if len(turns) == 1:
        return system, ad_types.get_text_content_as_str(turns[0]["content"])
    parts = ["The conversation so far:"]
    for m in turns:
        parts.append(f"<{m['role']}>\n{ad_types.get_text_content_as_str(m['content'])}\n</{m['role']}>")
    parts.append("Write the assistant's next reply.")
    return system, "\n\n".join(parts)


class ClaudeCLILLM(BasePipelineElement):
    """The privileged model: text in, text out."""

    def __init__(self, model):
        self.model = model
        self.name = f"claude-cli-{model}"

    def query(self, query, runtime, env=EmptyEnv(), messages=[], extra_args={}):
        system, prompt = render_transcript(messages)
        text = call_claude(system, prompt, self.model, role="privileged")
        reply = ad_types.ChatAssistantMessage(
            role="assistant", content=[ad_types.text_content_block_from_string(text)], tool_calls=None
        )
        return query, runtime, env, [*messages, reply], extra_args


_JSON = re.compile(r"\{.*\}", re.DOTALL)


def make_query_quarantined_llm(model, max_retries=3):
    """CaMeL's quarantined model with JSON prompting instead of native structured output.

    Mirrors camel.quarantined_llm.query_quarantined_llm: the same system prompt,
    the same added `have_enough_information` field, the same errors.
    """

    def query_quarantined_llm(llm, query, output_schema, retries=10):
        enough_information = (
            bool,
            Field(
                description="Whether the prompt provided **you** enough information to perform the task. It is **absolutely** imperative to set this to false if you don't have enough information to solve this task. Do not make assumptions of any sorts."
            ),
        )
        if issubclass(output_schema, BaseModel):
            output_model = create_model(
                output_schema.__name__, __base__=output_schema, have_enough_information=enough_information
            )
        else:
            output_model = create_model(
                "Result",
                output=(output_schema, Field(description="The requested value")),
                have_enough_information=enough_information,
            )
        system = (
            quarantined_llm._SYSTEM_PROMPT
            + "\nReply with only one JSON object that matches this JSON schema, and no other text:\n"
            + json.dumps(output_model.model_json_schema())
        )
        prompt = query
        for _ in range(min(retries, max_retries)):
            text = call_claude(system, prompt, model, role="quarantined")
            match = _JSON.search(text)
            try:
                res = output_model.model_validate_json(match.group(0) if match else text)
                break
            except ValidationError as e:
                prompt = f"{query}\n\nYour previous reply was not valid:\n{e}\nReply with only the JSON object."
        else:
            raise pydantic_ai.UnexpectedModelBehavior(f"Exceeded maximum retries ({max_retries}) for result validation")
        if not res.have_enough_information:
            raise quarantined_llm.NotEnoughInformationError()
        if issubclass(output_schema, BaseModel):
            return res
        return res.output

    query_quarantined_llm.__doc__ = quarantined_llm.query_quarantined_llm.__doc__
    return query_quarantined_llm


def install(model):
    """Route CaMeL's quarantined model calls through `claude -p`."""
    quarantined_llm.query_quarantined_llm = make_query_quarantined_llm(model)
