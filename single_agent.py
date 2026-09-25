"""Single agent system.

One LLM with access to both tools (web_search + python_calculator).
The LLM decides which tool to use and how many times.
The loop runs at most MAX_ATTEMPTS (5) LLM calls; if the model still
wants a tool after that, we stop.
"""

import json

from common import (
    MODEL,
    TOOL_CALCULATOR,
    TOOL_SEARCH,
    TokenTracker,
    call_llm,
    run_tool,
)

MAX_ATTEMPTS = 5
ALL_TOOLS = [TOOL_SEARCH, TOOL_CALCULATOR]

SYSTEM_PROMPT = """You are a helpful assistant that answers questions using tools.

You have two tools:
- web_search: search the web for current/real-world facts (prices, dates, populations, results...).
- python_calculator: evaluate a Python arithmetic expression to get an exact result.

Rules:
- Use web_search for any fact you don't know or that may have changed.
- Use python_calculator for ANY arithmetic, even simple math.
- You may use tools multiple times if needed.
- Once you have enough information, give a clear final answer with the reasoning and the numbers. Do NOT call tools just to say you're done.
"""


def run_single_agent(query: str, tracker: TokenTracker) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": query},
    ]

    for attempt in range(1, MAX_ATTEMPTS + 1):
        message = call_llm(messages, tools=ALL_TOOLS, tracker=tracker,
                           caller=f"agent:{attempt}")

        if message.tool_calls:
            print(f"  [attempt {attempt}] wants {len(message.tool_calls)} tool call(s): "
                  + ", ".join(f"{tc.function.name}({tc.function.arguments}) "
                              for tc in message.tool_calls))
            messages.append(message.model_dump(exclude_none=True))
            for tool_call in message.tool_calls:
                args = json.loads(tool_call.function.arguments)
                result = run_tool(tool_call.function.name, args)
                print(f"    -> {tool_call.function.name} returned: {result[:120]}...")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result),
                })
            continue

        # No tool calls -> final answer.
        print(f"  [attempt {attempt}] final answer")
        return message.content

    return ("Stopped: reached max attempts (5) without a final answer. "
            "Partial conversation kept.")


if __name__ == "__main__":
    query = input("Query: ")
    tracker = TokenTracker("single agent")
    answer = run_single_agent(query, tracker)
    print("\n=== ANSWER ===")
    print(answer)
    print("\n" + tracker.summary())
