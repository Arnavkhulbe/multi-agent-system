"""Shared pieces used by both the single-agent and multi-agent systems.

- call_llm: one Groq chat completion (OpenAI-compatible API), returns
  (message, tokens_used).
- tavily_search / python_calculator: the two tools.
- TokenTracker: sums prompt/completion tokens across every LLM call.
"""

import json
import os

from dotenv import load_dotenv
from openai import OpenAI
from tavily import TavilyClient

load_dotenv()

MODEL = "openai/gpt-oss-20b"

client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)
tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])


# ---------------------------------------------------------------- tools ----

TOOL_SEARCH = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": (
            "Search the web for current, real-world facts. Returns the top "
            "results with title, url and content snippet."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query"},
            },
            "required": ["query"],
        },
    },
}

TOOL_CALCULATOR = {
    "type": "function",
    "function": {
        "name": "python_calculator",
        "description": (
            "Evaluate a Python arithmetic expression and return the numeric "
            "result. Use this for any math instead of computing it yourself. "
            "Supports +, -, *, /, //, %, **, parentheses, and functions from "
            "the math module (sqrt, sin, cos, log, pi, e, ...)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A Python arithmetic expression, e.g. '1200 * 0.85 + 250'",
                },
            },
            "required": ["expression"],
        },
    },
}

tools_dict = {
    "web_search": TOOL_SEARCH,
    "python_calculator": TOOL_CALCULATOR,
}


def run_web_search(query: str) -> str:
    """Call the Tavily API and format results."""
    response = tavily.search(query=query, max_results=3)
    results = response.get("results", [])
    if not results:
        return "No results found."
    lines = []
    for r in results:
        lines.append(f"- {r['title']} ({r['url']}): {r['content'][:300]}")
    return "\n".join(lines)


def run_python_calculator(expression: str) -> str:
    """Evaluate a restricted Python arithmetic expression."""
    import math

    allowed_names = {
        name: getattr(math, name)
        for name in (
            "sqrt", "sin", "cos", "tan", "log", "log10", "log2", "exp",
            "floor", "ceil", "fabs", "pow", "pi", "e", "factorial",
        )
    }
    allowed_names["abs"] = abs
    try:
        result = eval(expression, {"__builtins__": {}}, allowed_names)  # noqa: S307 - restricted namespace
    except Exception as exc:  # noqa: BLE001 - report any error to the LLM
        return f"Error: {exc}"
    return f"{result}"


def run_tool(name: str, arguments: dict) -> str:
    if name == "web_search":
        return run_web_search(arguments["query"])
    if name == "python_calculator":
        return run_python_calculator(arguments["expression"])
    return f"Error: unknown tool '{name}'"


# ------------------------------------------------------------- llm call ----

class TokenTracker:
    """Accumulates token usage across all LLM calls."""

    def __init__(self, label: str):
        self.label = label
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0
        self.calls = 0
        self.per_call = []  # (caller, role, prompt, completion, total)

    def add(self, caller: str, usage) -> None:
        self.calls += 1
        p = getattr(usage, "prompt_tokens", 0) or 0
        c = getattr(usage, "completion_tokens", 0) or 0
        self.prompt_tokens += p
        self.completion_tokens += c
        self.total_tokens += p + c
        self.per_call.append((caller, p, c, p + c))

    def summary(self) -> str:
        lines = [f"=== Token usage: {self.label} ==="]
        for caller, p, c, t in self.per_call:
            lines.append(f"  {caller:<14} {p:>6} prompt + {c:>4} completion = {t:>6} total")
        lines.append(
            f"  TOTAL ({self.calls} calls): {self.prompt_tokens} prompt "
            f"+ {self.completion_tokens} completion = {self.total_tokens} tokens"
        )
        return "\n".join(lines)


def call_llm(
    messages: list,
    tools: list | None = None,
    tracker: TokenTracker | None = None,
    caller: str = "llm",
) -> object:
    """One chat completion against Groq. Returns the assistant message.

    Retries (resending the failed generation as an error) when the model
    produces a malformed tool call that Groq rejects with tool_use_failed.
    """
    kwargs = {"model": MODEL, "messages": messages}
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"
    response = None
    for _retry in range(5):
        try:
            response = client.chat.completions.create(**kwargs)
            break
        except Exception as exc:  # noqa: BLE001
            failed = ""
            body = getattr(exc, "body", None)
            if isinstance(body, dict):
                failed = body.get("failed_generation", "")
            if not failed or _retry == 4:
                raise
            # Feed the invalid generation back so the model can fix it.
            kwargs["messages"] = messages + [
                {"role": "assistant", "content": failed},
                {"role": "user", "content": (
                    "ERROR: that tool call was invalid (wrong tool name or "
                    "missing parameters). Call one of the provided tools "
                    "again with all required parameters."
                )},
            ]
    if tracker is not None:
        tracker.add(caller, response.usage)
    return response.choices[0].message
