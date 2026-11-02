# Write-up

## What I built
I built a command-line agent that takes a goal, like "competitive-landscape
brief for Notion", makes a plan, and then follows it step by step using two
tools: web search and a calculator. At the end it writes a short report. I
picked this goal because live data is easy to get from search, and it was
simple to test what happens when something fails.

## Why I built it this way
I kept the planner and the executor separate, so the plan is printed first
and you can see what the agent is about to do before it does it.

Early on the model sometimes sent back the plan in the wrong format and my
code crashed. So now the planner checks the plan and asks again if it looks
wrong.

When a tool fails, I send the error back to the model so it can try something
different. Without this it just repeated the same bad input. Each step gets
3 tries.

For the calculator I did not use `eval`, because it is unsafe. I used Python's
`ast` module so only basic math works.

I also made the report use only what the agent actually found. If something
is missing, it goes under Data Gaps. In one run the model had made up prices
for the calculator, so I fixed the prompt after that.

To test failures I added `--simulate-failure`. It makes the first search time
out, and then you can watch the agent recover in the log.

## What does not work well
- It reads only search snippets, not full pages, so numbers like users or
  revenue are often missing.
- Sometimes there is not much to calculate, because it depends on what the
  search finds.
- I did not write automated tests. I only tested by running it on a few
  different companies.
- Results change a bit from run to run.

## If I had more time
- Open the full pages instead of just snippets.
- Write proper tests for the planner check, the calculator and the retry logic.
- Check every number in the report against its source.
- Run it on 10 or more companies and count how often it fails.