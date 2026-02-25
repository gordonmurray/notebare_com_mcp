"""Notebare Facts MCP Server — calls the notebare.com API with a PAT."""

import os
from typing import Optional

import httpx
from mcp.server.fastmcp import FastMCP

API_URL = os.environ.get("NOTEBARE_API_URL", "https://api.notebare.com")
API_TOKEN = os.environ.get("NOTEBARE_API_TOKEN")
if not API_TOKEN:
    raise RuntimeError(
        "NOTEBARE_API_TOKEN env var is required. "
        "Create one at notebare.com or via POST /auth/tokens."
    )

mcp = FastMCP("notebare-facts")

_headers = {"Authorization": f"Bearer {API_TOKEN}"}


def _get_facts(domain: Optional[str] = None) -> list[dict]:
    """Fetch facts from the API. Returns [] on any error."""
    try:
        params = {}
        if domain:
            params["domain"] = domain
        resp = httpx.get(f"{API_URL}/facts/", headers=_headers, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return []


@mcp.tool()
def search_facts(
    domain: Optional[str] = None,
    tags: Optional[str] = None,
    min_confidence: Optional[float] = None,
) -> str:
    """Search the notebare facts store.

    Args:
        domain: Filter by exact domain name (e.g. "opensearch", "terraform").
        tags: Substring match against the tags field.
        min_confidence: Only return facts with confidence >= this value (0-1).
    """
    facts = _get_facts(domain=domain)
    if not facts:
        return "No facts found."

    # Client-side filters not supported by the API query params
    if min_confidence is not None:
        facts = [f for f in facts if (f.get("confidence") or 0) >= min_confidence]
    if tags is not None:
        facts = [f for f in facts if tags.lower() in (f.get("tags") or "").lower()]

    if not facts:
        return "No facts match the given filters."

    lines: list[str] = []
    for fact in facts:
        id_prefix = fact["id"][:8]
        conf_val = fact.get("confidence")
        conf = f"{conf_val:.0%}" if conf_val is not None else "n/a"
        tag_str = fact.get("tags") or ""
        source = fact.get("source") or ""
        created = str(fact.get("created_at", ""))[:10]
        lines.append(
            f"[{id_prefix}] {fact['domain']} | {conf} | {tag_str}\n"
            f"  {fact['statement']}\n"
            f"  {source} | {created}"
        )

    return f"{len(lines)} fact(s) found:\n\n" + "\n\n".join(lines)


@mcp.tool()
def list_domains() -> str:
    """List all fact domains with counts, sorted by most facts first."""
    facts = _get_facts()
    if not facts:
        return "No facts stored yet."

    counts: dict[str, int] = {}
    for f in facts:
        d = f.get("domain", "unknown")
        counts[d] = counts.get(d, 0) + 1

    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    total = sum(c for _, c in sorted_counts)
    items = "\n".join(f"  {domain}: {count} fact(s)" for domain, count in sorted_counts)
    return f"{total} domain(s):\n{items}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
