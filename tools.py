"""Custom Syrin tools for the Prode research pipeline."""

from syrin import tool
from syrin.tool import ToolSpec


@tool
async def duckduckgo_search(query: str, max_results: int = 5) -> str:
    """Search DuckDuckGo for a query and return formatted web results.

    Args:
        query: The search query string.
        max_results: Maximum number of results to return (default 5).

    Returns:
        A markdown-formatted string with search result titles, snippets, and URLs.
    """
    import aiohttp
    import asyncio

    search_url = "https://duckduckgo.com/html/"
    params = {"q": query, "kl": "en-us"}

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                search_url,
                params=params,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                html = await resp.text()
    except Exception:
        return ""

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    results = []

    for result in soup.find_all("a", class_="result__a", limit=max_results):
        title = result.get_text(strip=True)
        href = result.get("href", "")
        snippet_elem = result.find_parent("div", class_="result").find(
            "a", class_="result__snippet"
        )
        snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
        if title:
            results.append(f"**{title}**")
        if snippet:
            results.append(snippet)
        if href:
            results.append(f"Source: {href}")
        results.append("")

    if not results:
        return ""

    lines = ["## Recent Web Search Results\n"]
    lines.extend(results)
    return "\n".join(lines)


def _no_op_web_search(query: str) -> str:
    """No-op placeholder for Anthropic's native web_search tool.

    When using Anthropic provider, the model's built-in web_search tool is invoked
    directly by the provider. This placeholder exists because ToolSpec requires
    a callable func. The actual web search is handled by the model's own tool.
    """
    return "[web_search handled by provider natively]"


WEB_SEARCH_TOOL_SPEC = ToolSpec(
    name="web_search",
    description="Search the web for current information about a topic. Use this when you need up-to-date facts, data, or news that may not be in your training data.",
    parameters_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query. Be specific and include key terms.",
            }
        },
        "required": ["query"],
    },
    func=_no_op_web_search,
    returns="Search results with titles, snippets, and source URLs.",
)


@tool
def idea_context(idea: str) -> str:
    """Retrieve the research topic/idea being investigated.

    Args:
        idea: The user's original product idea.

    Returns:
        The idea string as-is, providing context to the agent.
    """
    return idea
