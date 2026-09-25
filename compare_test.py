"""Comparison test: run the same query through both agent systems."""

from common import TokenTracker
from single_agent import run_single_agent
from multi_agent import run_multi_agent

QUERY = (
    "What is the current population of Japan and the current population of "
    "Germany? Using those figures, calculate exactly how many more people "
    "live in Japan than Germany, and then calculate what percentage that "
    "difference is of Germany's population."
)


def main() -> None:
    print("=" * 70)
    print("QUERY:", QUERY)
    print("=" * 70)

    print("\n--- SINGLE AGENT ---")
    single_tracker = TokenTracker("single agent")
    single_answer = run_single_agent(QUERY, single_tracker)

    print("\n--- MULTI AGENT ---")
    multi_tracker = TokenTracker("multi agent")
    multi_answer = run_multi_agent(QUERY, multi_tracker)

    print("\n" + "=" * 70)
    print("SINGLE AGENT ANSWER:\n", single_answer)
    print("\nMULTI AGENT ANSWER:\n", multi_answer)
    print("\n" + single_tracker.summary())
    print("\n" + multi_tracker.summary())

    print("\n" + "=" * 70)
    print("COMPARISON")
    print(f"  {'':20}{'>Single':>10}{'Multi':>10}{'Diff':>10}")
    for label, attr in (("LLM calls", "calls"),
                        ("Input tokens", "prompt_tokens"),
                        ("Output tokens", "completion_tokens"),
                        ("Total tokens", "total_tokens")):
        s, m = getattr(single_tracker, attr), getattr(multi_tracker, attr)
        print(f"  {label:<20}{s:>10}{m:>10}{m - s:>+10}")


if __name__ == "__main__":
    main()
