Single vs Multi-Agent System
This project compares a Single-Agent and Multi-Agent architecture using the same task.
Architecture
The Single-Agent system uses one LLM with access to both Web Search and Calculator tools. The same agent decides which tool to use and generates the final answer.
The Multi-Agent system divides the work between a Manager Agent, Search Agent, and Maths Agent. The Manager coordinates the workflow, while the Search and Maths agents handle their specialized tasks. notes.txt acts as shared context between the agents.
Token Comparison
In the tested query:
Metric	Single-Agent	Multi-Agent
LLM Calls	5	8
Prompt Tokens	4,981	3,576
Completion Tokens	422	926
Total Tokens	5,403	4,502


Although Multi-Agent made more LLM calls, it used 901 fewer total tokens.
The main reason is that the Multi-Agent system works with more focused context, while the Single-Agent system carries a larger accumulated conversation and tool history across calls.
More LLM calls do not necessarily mean more tokens. Context size also plays a major role in token usage.
