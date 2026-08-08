# mcpinstall — Install the shared MCP servers (vm ⇄ ubuntu4)

> **Trigger**: `mcpinstall` | **Purpose**: Interactively install the MCP servers
> we host on **vm** and **ubuntu4** into the current machine's opencode config
> (`~/.config/opencode/opencode.jsonc`).
> **When to use**: The user types `mcpinstall` (or "install the mcps") and wants
> to wire up the cross-machine MCP servers.

---

## How It Works

We maintain **2 MCP servers on vm** and **2 on ubuntu4**. Each machine
typically wants the **other** machine's servers — so a vm user wants the 2
ubuntu4 MCPs, and an ubuntu4 user wants the 2 vm MCPs.

| Host | MCP server | Endpoint | Auth |
|------|-----------|----------|------|
| **vm** (`192.168.2.177`) | `secondbrain` (local stdio, from `~/second-brain`) | local stdio: `uv run python -m secondbrain.mcp_server` | none (local) |
| **vm** (`192.168.2.177`) | `secondbrain-net` (remote) | `http://192.168.2.177:8130/mcp` | none (LAN) |
| **ubuntu4** (`192.168.1.48`) | `agent-wiki` | `http://192.168.1.48:8908/mcp` | Bearer token |
| **ubuntu4** (`192.168.1.48`) | `agent-runtime` | `http://192.168.1.48:8914/mcp` | Bearer token |

Remote endpoint details + tokens live in the sibling guides (`ubuntu4agentwikimcp.md`,
`ubuntu4agentruntimemcp.md`, `vm-mcp-skills.md`).

---

## Phase 0 — Detect the current host

Determine whether this machine is **vm** or **ubuntu4**:

```bash
hostname   # → "vm" or "ubuntu4"
```

- On **vm** → the typical install is the **2 ubuntu4 MCPs** (`agent-wiki` +
  `agent-runtime`).
- On **ubuntu4** → the typical install is the **2 vm MCPs** (`secondbrain` +
  `secondbrain-net`).
- Confirm against `/etc/hostname` if `hostname` is ambiguous.

---

## Phase 1 — Ask via the question tool

Present an install menu with the **question tool**. Lead with the
`(Recommended)` option for the current host's typical install. Always include
an **Exit / Do nothing** option. **Never hand-craft question JSON.**

Example question for a **vm** user:

- **Install ubuntu4 MCPs (agent-wiki + agent-runtime)** `(Recommended)`
- **Install only agent-wiki**
- **Install only agent-runtime**
- **Install vm MCPs (secondbrain + secondbrain-net)** (unusual on vm)
- **Exit — no changes**

For an **ubuntu4** user, mirror the options:

- **Install vm MCPs (secondbrain + secondbrain-net)** `(Recommended)`
- **Install only secondbrain** (local stdio)
- **Install only secondbrain-net**
- **Install ubuntu4 MCPs (agent-wiki + agent-runtime)**
- **Exit — no changes**

Selecting an option is the trigger to perform the corresponding install below.

---

## Phase 2 — Install the selected server(s)

Edit **`~/.config/opencode/opencode.jsonc`**, adding/updating entries under the
existing `"mcp"` object. Preserve `$schema` and all existing fields. `type` is
required; `command` is an array of strings.

### vm MCPs

```jsonc
"secondbrain": {
  "type": "local",
  "command": ["uv", "--directory", "/home/paul/second-brain", "run", "python", "-m", "secondbrain.mcp_server"],
  "timeout": 30000,
  "enabled": true
},
"secondbrain-net": {
  "type": "remote",
  "url": "http://192.168.2.177:8130/mcp",
  "enabled": true
}
```

### ubuntu4 MCPs

```jsonc
"agent-wiki": {
  "type": "remote",
  "url": "http://192.168.1.48:8908/mcp",
  "enabled": true,
  "headers": { "Authorization": "Bearer <WIKI_MCP_TOKEN>" }
},
"agent-runtime": {
  "type": "remote",
  "url": "http://192.168.1.48:8914/mcp",
  "enabled": true,
  "headers": { "Authorization": "Bearer <RUNTIME_MCP_TOKEN>" }
}
```

> **Tokens**: pull the real token from the remote host's secret env, e.g.
> `grep WIKI_MCP_TOKEN /root/.secrets/wiki_mcp.env` (run on ubuntu4), then
> substitute into the header. Never commit the literal token to this repo.

---

## Phase 3 — Verify

1. Confirm `"enabled": true` and correct `"url"` for each added server.
2. For remote servers, hit `/health` or run the initialize probe from the
   guide to confirm reachability.
3. Tell the user to **quit and restart opencode** so the new MCP config loads
   (config is not hot-reloaded).

---

## Phase 4 — Report

List which servers were installed/enabled, the endpoint each points at, and
remind the user to restart opencode.
