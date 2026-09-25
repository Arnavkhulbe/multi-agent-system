"""Multi agent system (no LangGraph - plain Python loop).

- ask_manager_llm: the router. Decides which helper LLM to use next based on
  the original query and the notes file. Has NO tools itself.
- ask_search_llm: helper with access to ONLY the web_search tool.
- ask_maths_llm: helper with access to ONLY the python_calculator tool.

The manager keeps a notes file (notes.txt) where it records every helper
response. The loop runs at most MAX_ATTEMPTS (5) manager decisions.
"""

import json

from common import (
    TOOL_CALCULATOR,
    TOOL_SEARCH,
    TokenTracker,
    call_llm,
    run_tool,
)

MAX_ATTEMPTS = 5
NOTES_FILE = "notes.txt"

MANAGER_SYSTEM_PROMPT = """You are the MANAGER agent. Your ONLY job is to decide which helper agent to use next.

You cannot use tools yourself. Available helpers:
- "search": performs a web search (for current facts, prices, dates, numbers...).
- "maths": evaluates a Python arithmetic expression exactly.

Respond ONLY with JSON in this exact format:
{"helper": "search" | "maths" | "finish", "instruction": "<what you want the helper to do>", "reason": "<one short sentence>"}

If "helper" is "search", give the exact search query as instruction.
If "helper" is "maths", give the exact Python arithmetic expression as instruction.
If "helper" is "finish", put the final answer for the user in instruction.

Read the NOTES (results your helpers reported) before deciding. When the notes
contain everything needed to answer, choose "finish".
"""

SEARCH_SYSTEM_PROMPT = """You are the SEARCH helper agent. You have ONE tool: web_search.
Use it to find the information requested by the manager. You may search more
than once if the first results are not enough. Then report your findings as a
short factual summary with the key numbers. Never do arithmetic yourself.
"""

MATHS_SYSTEM_PROMPT = """You are the MATHS helper agent. You have ONE tool: python_calculator.
Use the calculator for the expression requested (or a corrected version if the
request has a typo). You may compute several expressions if useful. Then report
the result(s) clearly. Never invent numbers - always use the calculator tool.
"""


def read_notes() -> str:
    try:
        with open(NOTES_FILE, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "(no notes yet)"


def append_note(role: str, text: str) -> None:
    with open(NOTES_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{role}]\n{text}\n\n")


def reset_notes() -> None:
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        f.write("")


# ------------------------------------------------------------ ask_llm's ----

def ask_manager_llm(query: str, tracker: TokenTracker, attempt: int) -> dict:
    """Manager decides the next helper. Returns its JSON decision."""
    messages = [
        {"role": "system", "content": MANAGER_SYSTEM_PROMPT},
        {"role": "user", "content": (
            f"ORIGINAL QUERY:\n{query}\n\n"
            f"NOTES (helper responses so far):\n{read_notes()}\n\n"
            "Which helper should act next? Respond with the JSON decision only."
        )},
    ]
    message = call_llm(messages, tools=None, tracker=tracker,
                       caller=f"manager:{attempt}")
    content = message.content or "{}"
    # Tolerant JSON extraction (models sometimes wrap in ```json fences).
    content = content.strip()
    if content.startswith("```"):
        content = content.strip("`").removeprefix("json").strip()
    start, end = content.find("{"), content.rfind("}")
    decision = json.loads(content[start:end + 1])
    return decision


def _run_helper(system_prompt: str, tool_schema: list, task: str,
                helper_name: str, tracker: TokenTracker, attempt: int) -> str:
    """Shared helper loop: its own message list, may call its tool several times."""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Task from the manager: {task}"},
    ]
    for _ in range(MAX_ATTEMPTS):
        message = call_llm(messages, tools=tool_schema, tracker=tracker,
                           caller=f"{helper_name}:{attempt}")
        if not message.tool_calls:
            return message.content
        messages.append(message.model_dump(exclude_none=True))
        for tool_call in message.tool_calls:
            args = json.loads(tool_call.function.arguments)
            result = run_tool(tool_call.function.name, args)
            print(f"    [{helper_name}] {tool_call.function.name}({args}) -> {str(result)[:100]}...")
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result),
            })
    return "Helper reached max attempts without a final report."


def ask_search_llm(task: str, tracker: TokenTracker, attempt: int) -> str:
    return _run_helper(SEARCH_SYSTEM_PROMPT, [TOOL_SEARCH], task,
                       "search", tracker, attempt)


def ask_maths_llm(task: str, tracker: TokenTracker, attempt: int) -> str:
    return _run_helper(MATHS_SYSTEM_PROMPT, [TOOL_CALCULATOR], task,
                       "maths", tracker, attempt)


# ----------------------------------------------------------------- loop ----

def run_multi_agent(query: str, tracker: TokenTracker) -> str:
    reset_notes()
    for attempt in range(1, MAX_ATTEMPTS + 1):
        decision = ask_manager_llm(query, tracker, attempt)
        print(f"  [manager {attempt}] -> {decision['helper']}: "
              f"{decision.get('instruction', '')!r} ({decision.get('reason', '')})")

        if decision["helper"] == "finish":
            append_note("manager", f"FINAL ANSWER:\n{decision['instruction']}")
            return decision["instruction"]

        if decision["helper"] == "search":
            report = ask_search_llm(decision["instruction"], tracker, attempt)
        elif decision["helper"] == "maths":
            report = ask_maths_llm(decision["instruction"], tracker, attempt)
        else:
            report = f"Unknown helper '{decision['helper']}' - ignored."

        print(f"    [{decision['helper']} report] {str(report)[:120]}...")
        append_note(decision["helper"], f"Task: {decision['instruction']}\nReport: {report}")

    return ("Stopped: manager reached max attempts (5) without finishing. "
            f"Notes collected:\n{read_notes()}")


if __name__ == "__main__":
    query = input("Query: ")
    tracker = TokenTracker("multi agent")
    answer = run_multi_agent(query, tracker)
    print("\n=== ANSWER ===")
    print(answer)
    print(f"\n=== NOTES FILE ({NOTES_FILE}) ===")
    print(read_notes())
    print("\n" + tracker.summary())
