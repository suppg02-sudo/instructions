# Connecting Another IDE / Agent to Your Agent-Wiki MCP Server

This guide lets another machine (IDE, coding agent, or terminal MCP client) **read from and write to** your central agent-wiki — the shared knowledge store containing 250+ pages. The wiki is exposed as a Model Context Protocol (MCP) server over HTTP, so anything that speaks MCP can attach.

---

## 1. Connection Details (the only 3 things you need)

| Item | Value |
|------|-------|
| **MCP endpoint URL** | `http://192.168.1.48:8908/mcp` |
| **Transport** | Streamable HTTP (MCP spec) |
| **Auth** | Bearer token in `Authorization` header |
| **Server name (unique ID)** | `agent-wiki` |

> ⚠️ **IP is DHCP / may change**: `192.168.1.48` is currently assigned to the wiki host. If it stops working, re-ask the host for its current LAN IP and update the URL in your config. Both machine must be on the **same LAN / subnet** (e.g. `192.168.1.x`).

### Auth token
The remote client needs the same **Bearer token** your local config uses. Get it from the wiki host:

```bash
grep WIKI_MCP_TOKEN /root/.secrets/wiki_mcp.env
```

Send it as an HTTP header on every request:

```
Authorization: Bearer <WIKI_MCP_TOKEN>
```

---

## 2. Reachability Check (do this FIRST from the remote machine)

```bash
curl -i -X POST http://192.168.1.48:8908/mcp \
  -H "Authorization: Bearer <WIKI_MCP_TOKEN>" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe","version":"1.0"}}}'
```

A healthy response returns `serverInfo.name = "agent-wiki"` and the full tool list. If you see an error, see **Troubleshooting** below.

---

## 3. Add the Server to Your IDE / Client

Pick the section that matches your tool. All of these configure the *same* remote HTTP endpoint.

### A. VS Code / Cursor (`.vscode/mcp.json` at project root)

```json
{
  "servers": {
    "agent-wiki": {
      "type": "http",
      "url": "http://192.168.1.48:8908/mcp",
      "headers": {
        "Authorization": "Bearer <WIKI_MCP_TOKEN>"
      }
    }
  }
}
```

In Cursor, also add it via **Settings → MCP → Add new MCP server** with the same fields (type: `http`, URL + header).

### B. Cline / Roo Code (`.cline_mcp_settings.json` or Cline MCP manager)

```json
{
  "mcpServers": {
    "agent-wiki": {
      "type": "http",
      "url": "http://192.168.1.48:8908/mcp",
      "headers": {
        "Authorization": "Bearer <WIKI_MCP_TOKEN>"
      }
    }
  }
}
```

### C. Claude Code (`claude mcp add`)

```bash
claude mcp add agent-wiki \
  --transport http \
  http://192.168.1.48:8908/mcp \
  --header "Authorization: Bearer <WIKI_MCP_TOKEN>"
```

(For a project-scoped config, add `--scope project`.)

### D. opencode (`opencode.json`)

```jsonc
{
  "mcp": {
    "agent-wiki": {
      "type": "remote",
      "url": "http://192.168.1.48:8908/mcp",
      "enabled": true,
      "headers": {
        "Authorization": "Bearer <WIKI_MCP_TOKEN>"
      }
    }
  }
}
```

### E. Continue (`.continue/config.json` → `mcpServers`)

```json
{
  "mcpServers": [
    {
      "name": "agent-wiki",
      "type": "http",
      "url": "http://192.168.1.48:8908/mcp",
      "headers": {
        "Authorization": "Bearer <WIKI_MCP_TOKEN>"
      }
    }
  ]
}
```

---

## 4. Available Tools (what the remote agent can do)

### Read / Search (retrieve knowledge)
| Tool | Description |
|------|-------------|
| `wiki_read(slug)` | Read a full wiki page by slug |
| `wiki_search(query, limit?)` | Ranked full-text search across titles, summaries, tags, bodies |
| `wiki_index()` | Return the full wiki catalogue |
| `wiki_backlinks(slug)` | Find all pages referencing a page |
| `wiki_recent(days?)` | Pages updated in the last N days |
| `wiki_status()` | Wiki health: page counts, inbox depth |

### Write / Maintain (store knowledge)
| Tool | Description |
|------|-------------|
| `wiki_submit(content, source, metadata?)` | **Submit content to the wiki inbox** for audit — this is how the remote agent stores knowledge |
| `wiki_inbox_list(status?)` | List inbox items (pending / approved / rejected) |
| `wiki_inbox_review(inbox_id)` | Get full details of an inbox item |
| `wiki_inbox_approve(inbox_id, edits?)` | Approve an inbox item and write it to the wiki |
| `wiki_inbox_reject(inbox_id, reason?)` | Reject an inbox item |
| `wiki_audit_process(limit?)` | Run the audit loop on pending inbox items |

### Admin / Health
| Tool | Description |
|------|-------------|
| `wiki_lint(fix?)` | Run wiki health checks |
| `wiki_reindex()` | Rebuild full-text search and backlinks |
| `wiki_compile_system()` | Compile evolution artefacts into `wiki/system/` |
| `wiki_eval_run(name, baseline?)` | Run the golden eval set |
| `wiki_eval_report(run_id?)` | Get eval results for a run |

> **Recommended workflow for remote agents**: use `wiki_search`/`wiki_read` to pull context, and `wiki_submit` to add new knowledge (it lands in an inbox for review — the remote agent has an audit trail, not raw write access).

---

## 5. Verify the Connection from Your IDE

1. Open your IDE's **MCP server list** — `agent-wiki` should show **connected** (not error).
2. Run a simple tool, e.g. ask the agent to call `wiki_status()` or `wiki_search(query: "exposing an mcp server")`.
3. If the tool returns structured results (page count, search hits), you're wired up.

---

## 6. Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `401` / `unauthorized` | Wrong or missing token | Verify `Authorization: Bearer <token>` matches the host's `WIKI_MCP_TOKEN` |
| `421 Invalid Host header` | Host-header allowlist on the server rejects your LAN host | The server must list the wiki host's LAN IP in `WIKI_MCP_ALLOWED_HOSTS` (env file). **Already done for `192.168.1.48`.** If the host IP changed, update it on the server. |
| `Connection refused` / timeout | Wrong IP, or firewall blocking port `8908` | Confirm same subnet; on the host ensure `ufw`/firewall allows TCP `8908` from your client IP |
| `initialize` works but tools fail | Missing session (normal for raw curl, handled by IDEs) | IDE clients handle sessions automatically — this only affects hand-rolled scripts |
| "Server not found" / DNS | Old IP cached | Use the current LAN IP, not a stale one |
| `404` on read | Bad slug | Run `wiki_search` / `wiki_index` to get valid slugs first |

**On the wiki host**, the service is managed by systemd — check it if the remote cannot connect:

```bash
systemctl status wiki-mcp
systemctl restart wiki-mcp
```

---

## 7. Security Notes

- This exposes your wiki and its token to **anything on your LAN** that knows the URL+token. Only connect from trusted machines.
- The token (`WIKI_MCP_TOKEN`) is a bearer credential — **don't commit it** to a public repo or paste it in shared logs. Use your IDE's secret/`.env` handling where possible.
- DNS-rebinding protection is intentionally kept **enabled** on the server; `allowed_hosts` is the allowlist that makes LAN access work *without* disabling the protection.
