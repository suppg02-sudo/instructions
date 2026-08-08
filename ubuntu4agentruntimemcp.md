# Connecting Another IDE / Agent to the Agent-Runtime MCP Server

This guide lets another machine (IDE, coding agent, or terminal MCP client) **orient itself against this host's agent runtime** — the same behavior rules, trigger vocabulary, skills library, context files, agent definitions, and global menus that drive the local agent. Anything that speaks MCP can attach.

It is a complement to `ubuntu4agentwikimcp.md` (which exposes the *knowledge store*); this exposes the *runtime* that decides how to use that knowledge.

---

## 1. Connection Details

| Item | Value |
|------|-------|
| **MCP endpoint URL** | `http://192.168.1.48:8914/mcp` |
| **Transport** | Streamable HTTP (MCP spec) |
| **Auth** | Bearer token in `Authorization` header |
| **Server name (unique ID)** | `agent-runtime` |

> ⚠️ **IP is DHCP / may change**: `192.168.1.48` is the current LAN IP. Both machines must be on the **same LAN / subnet**. If it stops working, re-ask the host for its current IP and update the URL.

### Auth token
Get it from the agent-runtime host:

```bash
grep RUNTIME_MCP_TOKEN /root/.secrets/agent_runtime_mcp.env
```

Send it as a header on every request:

```
Authorization: Bearer <RUNTIME_MCP_TOKEN>
```

---

## 2. Reachability Check (do this FIRST from the remote machine)

```bash
curl -i -X POST http://192.168.1.48:8914/mcp \
  -H "Authorization: Bearer <RUNTIME_MCP_TOKEN>" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"probe","version":"1.0"}}}'
```

A healthy response sets a `mcp-session-id` header and returns `serverInfo.name = "agent-runtime"`.

---

## 3. Add the Server to Your IDE / Client

Same fields for every client: type = **http / remote**, URL above, plus an `Authorization: Bearer <token>` header.

### VS Code / Cursor (`.vscode/mcp.json`)
```json
{
  "servers": {
    "agent-runtime": {
      "type": "http",
      "url": "http://192.168.1.48:8914/mcp",
      "headers": { "Authorization": "Bearer <RUNTIME_MCP_TOKEN>" }
    }
  }
}
```

### Cline / Roo Code (`.cline_mcp_settings.json`)
```json
{
  "mcpServers": {
    "agent-runtime": {
      "type": "http",
      "url": "http://192.168.1.48:8914/mcp",
      "headers": { "Authorization": "Bearer <RUNTIME_MCP_TOKEN>" }
    }
  }
}
```

### Claude Code
```bash
claude mcp add agent-runtime \
  --transport http http://192.168.1.48:8914/mcp \
  --header "Authorization: Bearer <RUNTIME_MCP_TOKEN>"
```

### opencode (`opencode.json`)
```jsonc
{
  "mcp": {
    "agent-runtime": {
      "type": "remote",
      "url": "http://192.168.1.48:8914/mcp",
      "enabled": true,
      "headers": { "Authorization": "Bearer <RUNTIME_MCP_TOKEN>" }
    }
  }
}
```

### Continue (`.continue/config.json`)
```json
{
  "mcpServers": [
    { "name": "agent-runtime", "type": "http",
      "url": "http://192.168.1.48:8914/mcp",
      "headers": { "Authorization": "Bearer <RUNTIME_MCP_TOKEN>" } }
  ]
}
```

---

## 4. Available Tools

### Orientation (how to behave like this runtime)
| Tool | Description |
|------|-------------|
| `rt_rules(include_tools?)` | Global behavior rules (AGENTS.md); optionally the command-details reference |
| `rt_triggers(include_words?)` | Trigger vocabulary (triggers.yaml + trigger-words.md) — the intent/touch-point protocol |
| `rt_menus()` | Runtime-derived global menu options |
| `rt_intent()` | Accumulated intent log |

### Load & use skills
| Tool | Description |
|------|-------------|
| `rt_skills_list()` | All skills with name, version, description, tags, trigger |
| `rt_skills_search(query, limit?)` | Find skills by keyword (name/description/tags/trigger) |
| `rt_skills_read(name)` | Full SKILL.md for a skill |
| `rt_skills_file(name, rel_path)` | Read a reference file inside a skill (sandboxed — no path traversal) |

### Context files & agents
| Tool | Description |
|------|-------------|
| `rt_context_list()` | On-demand rule/context files (ag-triggers, ag-wiki-loop, ...) |
| `rt_context_read(name)` | Read a context file |
| `rt_agents_list()` | Agent/subagent definitions |
| `rt_agents_read(name)` | Read an agent definition |

### Write side (analytics parity)
| Tool | Description |
|------|-------------|
| `rt_trigger_record(name, context?)` | Record a trigger usage into this host's analytics, identical to local sessions |

> **Recommended remote-agent flow**: call `rt_rules()` and `rt_triggers()` once at session start to match behavior/touch-points, then `rt_skills_search` → `rt_skills_read` to load any skill, and `rt_context_read` for on-demand rules — mirroring how the local opencode runtime boots.

---

## 5. Verify

1. Your IDE's MCP list shows `agent-runtime` **connected**.
2. Run `rt_skills_list()` — expect ~90+ skills, e.g. `adguard`, `dashboard`...
3. Call `rt_rules()` — expect the host's AGENTS.md content.

---

## 6. Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `401` | Wrong/missing token | Check `Authorization: Bearer <RUNTIME_MCP_TOKEN>` matches the host env |
| `421 Invalid Host header` | Host-header allowlist | Host must list your LAN IP in `RUNTIME_MCP_ALLOWED_HOSTS` (env file) — done for `192.168.1.48` |
| `400` on tool call | Missing `mcp-session-id` (hand-rolled clients only) | IDEs handle sessions automatically; only raw scripts need it |
| `Connection refused` | Wrong IP / firewall `8914` | Confirm same subnet; host firewall must allow TCP `8914` |
| Unknown skill/context/agent in a read tool | Bad name | Use the corresponding `..._list` tool first for valid names |

On the host, manage via systemd:
```bash
systemctl status agent-runtime-mcp
systemctl restart agent-runtime-mcp
```

---

## 7. Security Notes

- Exposes the host's behavior config (rules, triggers, skills, context, agent defs) to anything on your LAN that knows the URL+token. Trusted machines only.
- `RUNTIME_MCP_TOKEN` is a bearer credential — **don't commit it** to public repos. Use `<RUNTIME_MCP_TOKEN>` placeholders and your IDE's secret handling.
- DNS-rebinding protection stays **enabled** server-side; the `RUNTIME_MCP_ALLOWED_HOSTS` allowlist enables LAN access without disabling it.
