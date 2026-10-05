CONVERT IT TO GITHUB README STYLE
Single vs Multi-Agent System
A Python project that compares a Single-Agent System with a Multi-Agent System using the same task, focusing on architecture, tool usage, context handling, LLM calls, and token consumption.

📌 Overview
This project demonstrates two approaches for solving the same problem with LLM agents.

Single-Agent
A single LLM has access to multiple tools and decides which tools to use.

User
  ↓
Single LLM
  ↓
 ┌───────────────┐
 │               │
Web Search    Calculator
 │               │
 └───────┬───────┘
         ↓
    Final Answer
Multi-Agent
Multiple specialized agents work together under the control of a Manager Agent.

                    User
                     ↓
                  Manager
                 /       \
                ↓         ↓
             Search     Maths
              Agent      Agent
                \         /
                 ↓       ↓
                 notes.txt
                     ↓
                  Manager
                     ↓
                Final Answer
🎯 Project Goal
The main goal is to understand the difference between:

A single LLM handling the entire task
Multiple specialized LLM agents collaborating
How context is passed between agents
How many LLM calls each architecture makes
How many tokens each architecture consumes
🤖 Single-Agent System
The Single-Agent system uses one LLM with access to both tools:

Web Search
Python Calculator
The LLM decides which tool to use and when.

Workflow
User Question
      ↓
Single LLM
      ↓
Web Search
      ↓
Single LLM
      ↓
Python Calculator
      ↓
Single LLM
      ↓
Final Answer
For the test query, the agent performed:

Search Japan population
Search Germany population
Calculate population difference
Calculate percentage difference
Generate final answer
🧠 Multi-Agent System
The Multi-Agent system divides the work between specialized agents.

Agents
Manager Agent
Responsible for deciding:

Which agent should work next
What task that agent should perform
Whether the task is complete
The Manager does not directly use the tools.

Search Agent
Responsible only for web searches.

Search Agent → Web Search
Maths Agent
Responsible only for calculations.

Maths Agent → Python Calculator
🔄 Multi-Agent Workflow
User Question
      ↓
   Manager
      ↓
  ┌───┴────┐
  ↓        ↓
Search    Maths
Agent     Agent
  ↓        ↓
Web       Calculator
Search
  ↓        ↓
  └───┬────┘
      ↓
  notes.txt
      ↓
   Manager
      ↓
    Finish
The project implements this orchestration using plain Python, without LangGraph.

📝 Shared Context
The Multi-Agent system uses:

notes.txt
as a shared workspace.

Different agents do not automatically share their private conversation history.

Therefore, the workflow is:

Search Agent
     ↓
Search Result
     ↓
notes.txt
     ↓
Manager
     ↓
Maths Agent
     ↓
Calculation Result
     ↓
notes.txt
     ↓
Manager
     ↓
Final Answer
notes.txt is not permanent LLM memory. It is simply a file used by the Python program to share relevant information between agents.

The Single-Agent system does not need this shared workspace because the same LLM maintains its conversation and tool history.

🛠️ Tools
The project uses two main tools.

Tool	Purpose
Web Search	Retrieve current information
Python Calculator	Perform mathematical calculations
Tool Access
System	Web Search	Calculator
Single-Agent	✅	✅
Manager Agent	❌	❌
Search Agent	✅	❌
Maths Agent	❌	✅
This demonstrates tool specialization in a Multi-Agent architecture.

📊 Token Usage Comparison
One of the main purposes of this project is to compare the token consumption of both architectures.

The same query was used for both systems:

What is the current population of Japan and the current population of Germany? Using those figures, calculate exactly how many more people live in Japan than Germany, and then calculate what percentage that difference is of Germany's population.

Results
Metric	Single-Agent	Multi-Agent
LLM Calls	5	8
Prompt Tokens	4,981	3,576
Completion Tokens	422	926
Total Tokens	5,403	4,502
🏆 Result
Single-Agent = 5,403 tokens
Multi-Agent  = 4,502 tokens
Difference:

5,403 - 4,502 = 901 tokens
Therefore, in this particular run:

Multi-Agent used 901 fewer total tokens than Single-Agent.

🔍 Why Did Multi-Agent Use Fewer Tokens?
An interesting observation is that Multi-Agent made more LLM calls:

Single-Agent → 5 calls
Multi-Agent  → 8 calls
Yet Multi-Agent consumed fewer total tokens.

The reason is that the number of LLM calls does not directly determine token usage.

Single-Agent
The Single-Agent system repeatedly carries its previous conversation and tool results.

Question
   ↓
LLM
   ↓
Search Result
   ↓
LLM + Previous Context
   ↓
Search Result
   ↓
LLM + Previous Context
   ↓
Calculator Result
   ↓
Final Answer
As the conversation grows, the prompt can become larger.

Single-Agent
Prompt Tokens      = 4,981
Completion Tokens  = 422
Total Tokens       = 5,403
Multi-Agent
The Multi-Agent system separates responsibilities and uses notes.txt as a shared workspace.

This allows agents to work with more focused information.

Multi-Agent
Prompt Tokens      = 3,576
Completion Tokens  = 926
Total Tokens       = 4,502
The Multi-Agent system therefore used:

4,981 - 3,576 = 1,405
fewer prompt tokens.

However, it generated:

926 - 422 = 504
more completion tokens because multiple agents need to communicate decisions and results.

⚖️ Key Trade-Off
The experiment demonstrates this trade-off:

Single-Agent
Fewer LLM calls
       ↓
Centralized reasoning
       ↓
Larger accumulated context
       ↓
Higher prompt token usage
Multi-Agent
More LLM calls
       ↓
Specialized responsibilities
       ↓
More focused context
       ↓
Lower prompt token usage
📁 Project Structure
multi-agent-system/
│
├── common.py
├── single_agent.py
├── multi_agent.py
├── compare_test.py
├── notes.txt
├── .gitignore
└── README.md
common.py
Contains shared functionality:

LLM client
Web search tool
Calculator tool
Tool definitions
Token tracking
LLM calling logic
single_agent.py
Implements the Single-Agent architecture.

multi_agent.py
Implements the Multi-Agent architecture:

Manager Agent
Search Agent
Maths Agent
Agent orchestration
Shared notes handling
compare_test.py
Runs the same query through both systems and compares:

LLM calls
Prompt tokens
Completion tokens
Total tokens
notes.txt
Acts as the shared workspace for the Multi-Agent system.

📈 Token Tracking
The project tracks:

Prompt Tokens
Completion Tokens
Total Tokens
The relationship is:

Total Tokens
=
Prompt Tokens + Completion Tokens
Token usage is recorded for individual LLM calls and then aggregated for each architecture.

⚙️ Technologies Used
Python
Groq
GPT-OSS-20B
OpenAI Python SDK
Tavily
python-dotenv
Python Calculator
🚀 Setup
1. Install Dependencies
pip install openai
pip install tavily-python
pip install python-dotenv

2. Create .env
Create a .env file in the project root:

GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
Never commit your .env file or API keys to GitHub.

▶️ Running the Project
Run Single-Agent
python single_agent.py

Run Complete Comparison
python compare_test.py

The comparison script runs the same query through both architectures and displays their token usage.

🎓 Learning Outcomes
This project demonstrates:

Single-Agent architecture
Multi-Agent architecture
Manager/Worker architecture
Agent specialization
Tool assignment
Shared context
LLM orchestration
Prompt tokens
Completion tokens
Total token usage
Token comparison
Context management
Trade-offs between centralized and distributed agent systems
⚠️ Important Note
The token results are based on a single experimental run.

LLM responses are stochastic, so token counts can change between runs depending on:

Query
Model response
Tool results
Number of iterations
Prompt structure
Output length
Therefore, the result:

Single-Agent → 5,403
Multi-Agent  → 4,502
should be interpreted as the result of this particular experiment, not as a universal rule.

🏁 Conclusion
This project demonstrates that more agents do not necessarily mean more token usage.

In the tested run:

Single-Agent → 5,403 tokens
Multi-Agent  → 4,502 tokens
The Multi-Agent system made more LLM calls but still consumed 901 fewer total tokens because each agent worked with more focused context.

The main takeaway is:

Single-Agent systems centralize reasoning, while Multi-Agent systems distribute responsibilities among specialized agents.

The better architecture depends on the task, complexity, context size, reliability requirements, latency, and token cost.
