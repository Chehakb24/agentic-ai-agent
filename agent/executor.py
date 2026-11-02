import json
from agent.llm import chat
from agent.tools.search import web_search
from agent.tools.calculator import calculator

TOOLS = {"web_search": web_search, "calculator": calculator}
MAX_RETRIES = 3

INPUT_SYSTEM = """You prepare the input for ONE tool call.
Return ONLY JSON: {"input": "..."}
- web_search: a short, specific search query (max 10 words).
- calculator: a plain math expression using only numbers and + - * / ** ( ),
  e.g. "(120-80)/80*100". Use real numbers from the context.
If a previous attempt failed, change your approach: use a different query or expression. Use ONLY numbers that appear in the collected results. Never invent or guess numbers.
If few numbers are available, calculate with just those."""

SYNTH_SYSTEM = """You write the final deliverable for an autonomous research agent.
Use ONLY facts present in the collected results. Do not add facts from your own memory.
If something is missing, list it under 'Data Gaps' instead of guessing.
Write a concise Markdown brief using headings and short bullet points (no big tables).
Sections: Overview, Key Competitors, Pricing, Strengths and Weaknesses, Takeaways, Data Gaps, Sources (URLs)."""

def _context(memory: list[dict], limit: int = 700) -> str:
    parts = []
    for m in memory:
        parts.append(f"Step {m['id']} ({m['tool']}): {m['description']}\nResult: {m['result'][:limit]}")
    return "\n\n".join(parts) or "(nothing collected yet)"


def _decide_input(goal, step, memory, last_error):
    prompt = (
        f"Goal: {goal}\n"
        f"Current step: {step['description']}\n"
        f"Tool: {step['tool']}\n"
        f"Collected so far:\n{_context(memory)}\n"
    )
    if last_error:
        prompt += f"\nPrevious attempt FAILED with: {last_error}\nTry a different input."
    raw = chat(INPUT_SYSTEM, prompt, json_mode=True)
    return json.loads(raw)["input"]


def run_step(goal, step, memory):
    tool_name = step["tool"]
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            tool_input = _decide_input(goal, step, memory, last_error)
            print(f"   attempt {attempt}: {tool_name}({tool_input!r})")
            result = TOOLS[tool_name](tool_input)
            print(f"   OK ({len(result)} chars)")
            return {"id": step["id"], "description": step["description"],
                    "tool": tool_name, "input": tool_input,
                    "result": result, "attempts": attempt, "status": "ok"}
        except Exception as e:
            last_error = f"{type(e).__name__}: {e}"
            print(f"   FAILED: {last_error}")
    return {"id": step["id"], "description": step["description"],
            "tool": tool_name, "input": None, "result": f"FAILED: {last_error}",
            "attempts": MAX_RETRIES, "status": "failed"}


def run_plan(goal, plan):
    memory = []
    print("\n=== EXECUTION ===")
    for step in plan:
        print(f"\n[{step['id']}] {step['description']}")
        if step["tool"] not in TOOLS:
            print("   (no tool needed, handled in final report)")
            continue
        memory.append(run_step(goal, step, memory))
    return memory


def synthesize(goal, memory):
    prompt = f"Goal: {goal}\n\nCollected results:\n{_context(memory, limit=1500)}"
    return chat(SYNTH_SYSTEM, prompt)
