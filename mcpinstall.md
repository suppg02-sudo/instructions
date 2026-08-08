# mcpinstall — Install the shared MCP servers (vm ⇄ ubuntu4)

> **Trigger**: `mcpinstall` | **Purpose**: Interactively install the MCP servers
> we host on **vm** and **ubuntu4** into the current machine's opencode config
> (`~/.config/opencode/opencode.jsonc`).
> **When to use**: The user types `mcpinstall` (or "install the mcps") and wants
> to wire up the cross-machine MCP servers.

---

## How It Works

Each host exposes **2 second-brain-flavoured MCP servers**. A machine typically
wants the **other** host's servers — so a vm user wants ubuntu4's 2, and an
ubuntu4 user wants vm's 2. The drives are the same on both boxes: one server is
**knowledge oriented**, the other is **skills / context oriented**.

| Host | Server | Orientation | Endpoint | Auth |
|------|--------|------------|----------|------|
| **vm** (`192.168.2.177`) | `secondbrain` | **Knowledge** (ingest/search/retrieve the graph) | `http://192.168.2.177:8130/mcp` (Streamable HTTP; legacy `/sse` also available) · local stdio `uv run python -m secondbrain.mcp_server` | none (LAN) |
| **vm** (`192.168.2.177`) | `secondbrain-skills` | **Skills / context** (list/get/select the opencode skills) | `http://192.168.2.177:8131/sse` (legacy SSE) | none (LAN) |
| **ubuntu4** (`192.168.1.48`) | `agent-wiki` | **Knowledge** (wiki pages store) | `http://192.168.1.48:8908/mcp` | Bearer token |
| **ubuntu4** (`192.168.1.48`) | `agent-runtime` | **Skills / context** (rules, triggers, skills, context, agent defs) | `http://192.168.1.48:8914/mcp` | Bearer token |

Remote endpoint details + tokens live in the sibling guides
(`ubuntu4agentwikimcp.md`, `ubuntu4agentruntimemcp.md`, `vm-mcp-skills.md`).

---

## Phase 0 — Detect the current host

Determine whether this machine is **vm** or **ubuntu4**:

```bash
hostname   # → "vm" or "ubuntu4"
```

- On **vm** → the typical install is the **2 ubuntu4 MCPs** (`agent-wiki` +
  `agent-runtime`).
- On **ubuntu4** → the typical install is the **2 vm MCPs** (`secondbrain` +
  `secondbrain-skills`).
- Confirm against `/etc/hostname` if `hostname` is ambiguous.

---

## Phase 1 — Ask via the question tool

Present an install menu with the **question tool**. Lead with the
`(Recommended)` option for the current host's typical install. Always include
an **Exit / Do nothing** option. **Never hand-craft question JSON.**

Example question for a **vm** user:

- **Install ubuntu4 MCPs (agent-wiki + agent-runtime)** `(Recommended)`
- **Install only agent-wiki** (knowledge)
- **Install only agent-runtime** (skills / context)
- **Install local vm MCPs (secondbrain + secondbrain-skills)** (unusual on vm)
- **Exit — no changes**

For an **ubuntu4** user, mirror the options:

- **Install vm MCPs (secondbrain + secondbrain-skills)** `(Recommended)`
- **Install only secondbrain** (knowledge)
- **Install only secondbrain-skills** (skills / context)
- **Install ubuntu4 local MCPs (agent-wiki + agent-runtime)**
- **Exit — no changes**

Selecting an option is the trigger to perform the corresponding install below.

---

## Phase 2 — Install the selected server(s)

Edit **`~/.config/opencode/opencode.jsonc`**, adding/updating entries under the
existing `"mcp"` object. Preserve `$schema` and all existing fields. `type` is
required; `command` is an array of strings.

### vm MCPs (knowledge + skills)

```jsonc
"secondbrain": {
  "type": "remote",
  "url": "http://192.168.2.177:8130/mcp",
  "enabled": true
},
"secondbrain-skills": {
  "type": "remote",
  "url": "http://192.168.2.177:8131/sse",
  "enabled": true
}
```

> If installed on **vm itself** (local), prefer the stdio form for
> `secondbrain` instead of `remote`:
> ```jsonc
> "secondbrain": {
>   "type": "local",
>   "command": ["uv", "--directory", "/home/paul/second-brain", "run", "python", "-m", "secondbrain.mcp_server"],
>   "timeout": 30000,
>   "enabled": true
> }
> ```

### ubuntu4 MCPs (knowledge + skills / context)

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
   relevant guide to confirm reachability.
3. Tell the user to **quit and restart opencode** so the new MCP config loads
   (config is not hot-reloaded).

---

## Phase 4 — Report

List which servers were installed/enabled, the endpoint and orientation
(knowledge vs skills) of each, and remind the user to restart opencode.
