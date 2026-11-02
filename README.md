# Competitive Landscape Agent

This is my sybmission for the position of agentic AI Intern position at Xiarch Bharat I built a small agent that takes a goal in plain English, makes a plan, uses web search and a calculator, retries when something break off 
 and also writes a final  report.

Built for the Agentic AI Engineer Intern take-home.

## What it does

1. Takes a goal (I used "competitive-landscape brief for <company>").
2. Planner (LLM) breaks it into 4-6 steps and prints the plan first.
3. Executor runs each step with a tool:
   - `web_search`: DuckDuckGo (live data, no dataset)
   - `calculator`: safe math evaluator (no `eval`)
4. If a step fails, the agent retries up to 3 times with a different input.
5. At the end it writes a Markdown report with sources and data gaps.

## Setup

```
git clone <your-repo-url>
cd agentic-intern
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Make a `.env` file in the project folder:

```
GROQ_API_KEY=your_key_here
```

Free key: https://console.groq.com

## Run

```
python main.py "Produce a short competitive-landscape brief for Notion"
```

Failure demo (the first search call times out on purpose):

```
python main.py "Produce a short competitive-landscape brief for Figma" --simulate-failure
```

## Project structure

```
main.py              CLI entry
agent/
  llm.py             Groq wrapper (model: openai/gpt-oss-120b)
  planner.py         goal -> steps, validates the plan, retries if invalid
  executor.py        runs steps, retry logic, final report
  tools/
    search.py        web search (+ simulated failure switch)
    calculator.py    safe calculator
samples/             sample run logs
```
## Problems I ran into while building

- Model 404: My first model, suddenly gave a 404 error
  because Groq no longer had it. I checked their current list and moved to
  `openai/gpt-oss-120b`.
- Plan crashed the code: Once the LLM sent the plan steps as plain strings
  instead of objects, and my code broke with a TypeError. So I added a check in
  the planner. If the plan looks wrong, it asks the model again.
- Calculator problems: The first time, the LLM passed a sentence to the
  calculator instead of a math expression, and it failed. The agent retried and
  fixed it by itself, which was nice to see. Later I noticed it was using prices
  that were never in the search results, so I changed the prompt to only allow
  numbers from the collected data.


## How failures are handled

- Tool fails or returns nothing: the error message goes back to the LLM
  and it tries again with a different query or expression. Each step gets
  3 attempts at most.
- Bad plan from the LLM: the planner checks the plan first. If it is
  broken, it asks the model again.
- Still failing after 3 attempts: the step is marked as failed and the
  final report mentions it under Data Gaps, instead of guessing an answer.
- Testing it: running with `--simulate-failure` makes the first search
  throw a timeout on purpose, so you can see the agent recover in the log.
## Assumptions

- No dataset used. All data comes from live web search at run time.
- Search snippets are short, so some numbers (users, revenue) can be missing.
  The report says so instead of guessing.

## Limitations

- Only search snippets are read, not full web pages.
- No unit tests yet.

## Sample runs

See the `samples/` folder:
- `run1_notion.txt`
- `run2_zomato.txt`
- `run3_figma_failure.txt` (with the induced failure)