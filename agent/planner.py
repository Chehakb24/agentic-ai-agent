import json
from agent.llm import chat

VALID_TOOLS = {"web_search", "calculator", "none"}

SYSTEM = """You are a planning module of an autonomous research agent.
Break the user's goal into 4-6 concrete steps.
Available tools: web_search, calculator.
Rules:
- Use web_search to gather facts.
- You MUST include at least one calculator step that computes something
  from gathered numbers (e.g. price differences, percentages, averages).
- The last step must use tool "none" to write the final brief.
- Every step must be an object with keys: id, description, tool.
Return ONLY JSON in this format:
{"steps": [{"id": 1, "description": "...", "tool": "web_search"}]}
"""


def _clean(steps):
    # har step dict hona chahiye, tool valid hona chahiye
    if not isinstance(steps, list) or len(steps) < 2:
        raise ValueError("plan too short or not a list")
    cleaned = []
    for i, s in enumerate(steps, start=1):
        if not isinstance(s, dict):
            raise ValueError(f"step {i} is not an object")
        if s.get("tool") not in VALID_TOOLS or not s.get("description"):
            raise ValueError(f"step {i} has bad tool or description")
        cleaned.append({"id": i, "description": s["description"], "tool": s["tool"]})
    return cleaned


def make_plan(goal: str, tries: int = 3) -> list[dict]:
    last_err = None
    for _ in range(tries):
        try:
            raw = chat(SYSTEM, f"Goal: {goal}", json_mode=True)
            return _clean(json.loads(raw)["steps"])
        except Exception as e:
            last_err = e
            print(f"(plan invalid, retrying: {e})")
    raise RuntimeError(f"Could not build a valid plan: {last_err}")