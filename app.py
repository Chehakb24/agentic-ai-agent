import streamlit as st
import agent.tools.search as search_tool
from agent.planner import make_plan
from agent.executor import run_plan, synthesize

st.set_page_config(page_title="Competitive Landscape Agent")
st.title("Competitive Landscape Agent")
st.write("Give a goal. The agent plans, uses tools, retries on failure, and writes a report.")

goal = st.text_input(
    "Goal",
    "Produce a short competitive-landscape brief for Notion",
)
fail = st.checkbox("Simulate a search failure (first search times out)")

if st.button("Run agent") and goal.strip():
    search_tool.SIMULATE_FAILURE = fail
    search_tool._calls = 0  # reset so the failure happens on every run

    with st.spinner("Planning..."):
        plan = make_plan(goal)

    st.subheader("Planning trace")
    for step in plan:
        st.write(f"**{step['id']}.** {step['description']}  `{step['tool']}`")

    with st.spinner("Running the steps, this can take a minute..."):
        memory = run_plan(goal, plan)

    st.subheader("Execution")
    for m in memory:
        label = f"Step {m['id']} ({m['tool']}): {m['status']}, attempts: {m['attempts']}"
        with st.expander(label):
            st.write(f"Input: `{m['input']}`")
            st.text(m["result"][:1500])

    with st.spinner("Writing the report..."):
        report = synthesize(goal, memory)

    st.subheader("Final report")
    st.markdown(report)