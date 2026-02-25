# notebare.com MCP Server

An MCP server that connects your [notebare.com](https://notebare.com) facts store to [Claude Code](https://claude.ai/download) via the Model Context Protocol.

Once configured, Claude can search your notebare knowledge base during conversations.

## Prerequisites

- Python 3.10 or later
- Claude Code installed and working
- A notebare.com account with at least one fact saved

## Setup

### 1. Create an API Token

Log in to [notebare.com](https://notebare.com), go to Projects, and scroll down to the **API Tokens** section. Create a token and copy it immediately — it won't be shown again.

### 2. Install

```bash
git clone https://github.com/gordonmurray/notebare_com_mcp.git
cd notebare_com_mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure `.mcp.json`

Add the following to your project's `.mcp.json` (or `~/.claude/.mcp.json` for global access). Replace the placeholders with your actual values:

```json
{
  "mcpServers": {
    "notebare-facts": {
      "command": "/path/to/notebare_com_mcp/.venv/bin/python",
      "args": ["/path/to/notebare_com_mcp/server.py"],
      "env": {
        "NOTEBARE_API_TOKEN": "nb_your_token_here",
        "NOTEBARE_API_URL": "https://api.notebare.com"
      }
    }
  }
}
```

### 4. Verify

Restart Claude Code. You should see the `notebare-facts` MCP server connect. Try:

```
"List my notebare domains"
"Search my notebare facts about terraform"
```

## Tools

### `search_facts`

Search the notebare facts store.

| Parameter | Type | Description |
|-----------|------|-------------|
| `domain` | string, optional | Filter by exact domain name, e.g. "terraform" |
| `tags` | string, optional | Substring match against the tags field |
| `min_confidence` | float, optional | Only return facts with confidence >= this value (0-1) |

### `list_domains`

List all fact domains with counts, sorted by most facts first. Takes no parameters.

## License

Apache 2.0
