Single vs Multi-Agent System


This project compares a Single-Agent and Multi-Agent system using the same task. The Single-Agent system uses one LLM with access to both Web Search and Calculator tools. The Multi-Agent system divides the work between a Manager Agent, Search Agent, and Maths Agent, with notes.txt used to share context between agents.


In the test, the Single-Agent used 5,403 tokens, while the Multi-Agent used 4,502 tokens. Even though the Multi-Agent made more LLM calls, it used 901 fewer tokens because each agent worked with more focused context, while the Single-Agent carried more conversation and tool history between calls.



More LLM calls do not necessarily mean more token usage. Context size also matters.
