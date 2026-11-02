import sys
from agent.planner import make_plan
from agent.executor import run_plan, synthesize


def main():
    if len(sys.argv) < 2:
        print('Usage: python main.py "your goal here"')
        return

    import agent.tools.search as s
    if "--simulate-failure" in sys.argv:
        sys.argv.remove("--simulate-failure")
        s.SIMULATE_FAILURE = True

    goal = " ".join(sys.argv[1:])
    print(f"\nGOAL: {goal}\n")

    print("=== PLANNING TRACE ===")
    plan = make_plan(goal)
    for step in plan:
        print(f"[{step['id']}] {step['description']}  (tool: {step['tool']})")

    memory = run_plan(goal, plan)

    print("\n=== FINAL REPORT ===\n")
    print(synthesize(goal, memory))


if __name__ == "__main__":
    main()