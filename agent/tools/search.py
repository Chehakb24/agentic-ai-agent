try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS


def web_search(query: str, max_results: int = 5) -> str:
    with DDGS() as d:
        results = list(d.text(query, max_results=max_results))
    if not results:
        raise ValueError(f"No search results for: {query}")
    return "\n".join(
        f"- {r['title']}: {r['body']} ({r['href']})" for r in results
    )