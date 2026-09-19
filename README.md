# Multi-Agent Research System

A multi-agent AI research pipeline that searches the web, extracts detailed information from relevant sources, writes a structured research report, and reviews the final report using an AI critic.

The system uses:

* LangChain
* OpenAI
* Tavily Search
* BeautifulSoup
* Requests
* Tool-calling agents
* Prompt chains

---

## Overview

This project implements a sequential multi-agent research workflow.

The system takes a research topic from the user and passes it through multiple specialized components:

1. Search Agent
2. Information Agent
3. Writer Agent
4. Critic Agent

Each component has a separate responsibility.

---

## Architecture

```text
                    User Query
                        |
                        v
                +----------------+
                |  Search Agent  |
                +----------------+
                        |
                        v
                 Tavily Search
                        |
                        v
               Search Results
                        |
                        v
              +-------------------+
              | Information Agent |
              +-------------------+
                        |
                        v
                get_information()
                        |
                        v
                 Web Scraping
                        |
                        v
              Detailed Research
                        |
                        v
                +--------------+
                | Writer Agent |
                +--------------+
                        |
                        v
                Research Report
                        |
                        v
                +--------------+
                | Critic Agent |
                +--------------+
                        |
                        v
                Review + Score
```

---

## Multi-Agent Workflow

```text
User Topic
   |
   v
Search Agent
   |
   | get_search()
   v
Recent Search Results
   |
   v
Information Agent
   |
   | get_information()
   v
Detailed Web Content
   |
   v
Writer Agent
   |
   v
Structured Research Report
   |
   v
Critic Agent
   |
   v
Feedback + Score
```

---

## Agents

### 1. Search Agent

The Search Agent finds recent and relevant information about the user's topic.

It uses the Tavily Search API through the `get_search` tool.

```python
def search_agent():
    return create_agent(
        model=model,
        tools=[get_search]
    )
```

Its responsibility is:

```text
User Topic
     |
     v
Search Agent
     |
     v
get_search()
     |
     v
Tavily API
     |
     v
URLs + Titles + Snippets
```

The search tool returns:

```text
URL
Title
Snippet
```

for each search result.

---

### 2. Information Agent

The Information Agent receives the search results and chooses a relevant URL for deeper research.

```python
def info_agent():
    return create_agent(
        model=model,
        tools=[get_information]
    )
```

The agent uses:

```text
get_information()
```

to download and extract text from a webpage.

Its workflow is:

```text
Search Results
      |
      v
Information Agent
      |
      v
Select Relevant URL
      |
      v
get_information()
      |
      v
requests
      |
      v
BeautifulSoup
      |
      v
Clean Web Content
```

---

## Tools

### get_search

The `get_search` tool searches the internet using Tavily.

```python
@tool
def get_search(query: str) -> str:
```

It returns up to five search results containing:

```text
URL
Title
Snippet
```

---

### get_information

The `get_information` tool extracts the main text from a webpage.

```python
@tool
def get_information(url: str) -> str:
```

It uses:

```text
requests
+
BeautifulSoup
```

The tool removes unnecessary HTML elements such as:

```text
script
style
noscript
```

and returns cleaned webpage text.

---

## Writer Agent

The Writer component receives both:

```text
Search Results
+
Detailed Research
```

and generates a structured research report.

The report contains:

```text
Introduction

Key Findings
- Finding 1
- Finding 2
- Finding 3

Conclusion

Sources
```

The writer pipeline is:

```python
writer_chain = (
    writer_prompt
    | model
    | StrOutputParser()
)
```

The Writer Agent is responsible for converting raw research into readable and structured information.

---

## Critic Agent

The Critic Agent evaluates the generated report.

It analyzes:

```text
Research Report
      |
      v
Critic
      |
      v
Score
Strengths
Areas to Improve
Verdict
```

The critic returns output in the following format:

```text
Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
...
```

The critic pipeline is:

```python
critic_chain = (
    critic_prompt
    | model
    | StrOutputParser()
)
```

---

## Orchestrator

The main orchestration logic is handled by:

```python
get_research()
```

This function coordinates the complete pipeline.

```text
get_research(topic)
        |
        +---- Search Agent
        |
        +---- Information Agent
        |
        +---- Combine Research
        |
        +---- Writer Agent
        |
        +---- Critic Agent
        |
        v
Final State
```

The final state contains:

```python
{
    "search_result": "...",
    "research_result": "...",
    "report": "...",
    "feed_back": "..."
}
```

---

## Execution Flow

When the program starts:

```python
inp = input("Make your research ")
```

the topic is passed to:

```python
get_research(inp)
```

The execution order is:

```text
1. User enters topic

2. Search Agent searches the web

3. Search results are stored

4. Information Agent selects and scrapes a relevant source

5. Search and scraped information are combined

6. Writer generates the report

7. Critic reviews the report

8. Final report is printed

9. Critic feedback is printed
```

---

## Project Structure

A cleaner production structure could be:

```text
multi-agent-research/
│
├── main.py
│
├── agents/
│   ├── search_agent.py
│   ├── information_agent.py
│   ├── writer_agent.py
│   └── critic_agent.py
│
├── tools/
│   ├── search_tool.py
│   └── scraping_tool.py
│
├── prompts/
│   ├── writer_prompt.py
│   └── critic_prompt.py
│
├── services/
│   └── research_service.py
│
├── .env
├── requirements.txt
├── .gitignore
└── README.md
```

For the current single-file version:

```text
multi-agent-research/
│
├── main.py
├── .env
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Requirements

Install the required libraries:

```bash
pip install langchain langchain-openai tavily-python beautifulsoup4 requests python-dotenv
```

Or using `uv`:

```bash
uv pip install langchain langchain-openai tavily-python beautifulsoup4 requests python-dotenv
```

---

## Environment Variables

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key
```

The application requires both APIs.

---

## Running the Project

Run:

```bash
python main.py
```

Then enter a research topic:

```text
Make your research: Latest developments in Agentic AI
```

The system will execute:

```text
Scraping URLs...
Gathering information...
Writing report...
Reviewing report...
```

and finally return the generated research report and critic feedback.

---

## Example Pipeline

Input:

```text
Latest developments in Agentic AI
```

Pipeline:

```text
Latest developments in Agentic AI
              |
              v
         Search Agent
              |
              v
        Tavily Search
              |
              v
       Search Results
              |
              v
     Information Agent
              |
              v
       Webpage Scraping
              |
              v
        Research Data
              |
              v
         Writer Agent
              |
              v
       Research Report
              |
              v
         Critic Agent
              |
              v
      Score + Feedback
```

---

## Error Handling

The research pipeline contains error handling for both search and scraping.

If search fails:

```python
state["search_result"] = f"Search failed: {e}"
```

If webpage extraction fails:

```python
state["research_result"] = f"Scraping failed: {e}"
```

This prevents the complete application from crashing when one external operation fails.

---

## Agent Responsibilities

| Component         | Responsibility                                 |
| ----------------- | ---------------------------------------------- |
| Search Agent      | Find recent and reliable web sources           |
| Information Agent | Extract deeper information from a relevant URL |
| Writer Agent      | Convert research into a structured report      |
| Critic Agent      | Review report quality and provide feedback     |
| Orchestrator      | Control the complete agent workflow            |

---

## Current Architecture Type

This project currently uses a:

```text
Sequential Multi-Agent Pipeline
```

rather than a fully autonomous multi-agent architecture.

The execution path is predefined:

```text
Search
  ↓
Information Extraction
  ↓
Writer
  ↓
Critic
```

Agents do not independently communicate with each other. The `get_research()` function acts as the central orchestrator and transfers results between components.

---

## Possible Advanced Architecture

The project can later be upgraded to LangGraph:

```text
                    START
                      |
                      v
                  Researcher
                      |
                      v
                 Web Scraper
                      |
                      v
                   Writer
                      |
                      v
                   Critic
                  /      \
             Approved   Improve
                |          |
                v          |
               END <--- Writer
```

With this architecture, the Critic Agent could send bad reports back to the Writer Agent automatically.

For example:

```text
Writer
  |
  v
Critic
  |
  +---- Score >= 8 ----> END
  |
  +---- Score < 8 -----> Writer
```

This would turn the current sequential pipeline into an iterative multi-agent workflow.

---

## Future Improvements

The system can be extended with:

```text
LangGraph state management
Multiple URL scraping
Parallel research agents
Source verification
Structured output
Retry mechanisms
Caching
Memory
Human approval
Writer-Critic feedback loop
Citation validation
Research confidence scoring
Observability with LangSmith
Async tool execution
Rate limiting
```

---

## Tech Stack

```text
Python
LangChain
OpenAI
Tavily
BeautifulSoup
Requests
```

---

## Conclusion

This project demonstrates a modular multi-agent research workflow where specialized AI components cooperate to perform different stages of a research task.

The architecture separates:

```text
Searching
Research Extraction
Writing
Evaluation
```

into independent components, making the system easier to maintain and extend.

The current architecture provides a strong base for moving toward more advanced Agentic AI systems using LangGraph, persistent state, parallel agents, feedback loops, and dynamic routing.
