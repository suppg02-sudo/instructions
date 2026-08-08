# Remote MCP Client — Connect Another IDE to the Second Brain

> How to connect an IDE/agent on **another LAN PC** (Cursor, W&B, VSCode via
> Cline/Roo, Windsurf, another opencode, LibreChat, etc.) to this box's Second
> Brain knowledge runtime for **storing** and **retrieving** knowledge.

**Box (this machine):** LAN IP `192.168.2.177` · hostname `vm`

**Recommended path:** use the **already-running MCP server** on port 8130. It
proxies to the runtime API *on this box*, so the remote client needs **no code,
no packages, no repo checkout** — just point its MCP client at one URL. The same
process exposes **both** modern transports:

- **Streamable HTTP (preferred, modern):** `http://192.168.2.177:8130/mcp`
- **Legacy SSE (fallback):** `http://192.168.2.177:8130/sse`

---

## 0. Prerequisites / reachability

- Make sure you can reach the box from the other PC:
  ```bash
  curl -s http://192.168.2.177:8000/health    # runtime API        → {"status":"ok"}
  curl -s http://192.168.2.177:8130/health    # MCP (both)         → {"status":"ok","transport":"sse|streamable-http",...}
  curl -s -X POST http://192.168.2.177:8130/mcp \
       -H 'Content-Type: application/json' \
       -H 'Accept: application/json, text/event-stream' \
       -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"t","version":"1"}}}'
  ```
- The MCP service runs as a systemd **user** unit on the box:
  `secondbrain-sse.service` (port 8130, binding `0.0.0.0`, Streamable HTTP at
  `/mcp` + legacy SSE at `/sse` on the same process).
- **No auth token** is currently required. The LAN endpoint is open. If the LAN
  is trusted (home network) this is fine; see §6 to lock it down if not.

---

## 1. The URLs to give your IDE

**Preferred (Streamable HTTP):**
```
http://192.168.2.177:8130/mcp
```
**Fallback (legacy SSE):**
```
http://192.168.2.177:8130/sse
```

Transport: **Streamable HTTP** (`/mcp`) is the modern standard and what
Cline/Roo/VSCode/current clients speak; **legacy SSE** (`/sse`) is kept for
LibreChat and older clients. Both run on the same 8130 process. Register the
`/mcp` URL first; drop to `/sse` only if a specific client requires it.

Tools exposed (both transports): `knowledge_ingest`, `knowledge_search`,
`knowledge_lookup`, `knowledge_query`, `knowledge_topic`, `knowledge_ingest_url`,
`knowledge_job`, `knowledge_export`, `knowledge_import`, `knowledge_enrich`,
`knowledge_consolidate`, `knowledge_prune`, `knowledge_reindex`,
`knowledge_delete_note`, `knowledge_topic_curate`, `knowledge_research`.

---

## 2. Registering it in common IDEs

### Cursor
`Cursor Settings → MCP → Add new MCP server` →
- **Type:** Streamable HTTP
- **Name:** `secondbrain` (or whatever)
- **URL:** `http://192.168.2.177:8130/mcp`
Save. Cursor lists the `knowledge_*` tools (look for a green "connected").
Cursor needs to run with an agent model to invoke the tools.

### Windsurf
`Settings → MCP Servers → +` → choose **Streamable HTTP** → enter the `/mcp` URL.

### VSCode + Cline / Roo Code (or vscode-mcp)
In the *mcp.json* / `~/.vscode/mcp.json` of the other machine:
```json
{
  "mcpServers": {
    "secondbrain": {
      "type": "http",
      "url": "http://192.168.2.177:8130/mcp"
    }
  }
}
```
Streamable HTTP is natively supported here — no stdio-over-SSH workaround
needed. If a client still reports a handshake failure, fall back to `Type: sse`
with the `/sse` URL.

### LibreChat (self-hosted web)
Register an **MCP server of type `sse`** pointing at
`http://192.168.2.177:8130/sse` (LibreChat's Docker setup uses SSE).

### opencode / pi on the box itself
These should already be wired (MCP over stdio). Only relevant if you want *this*
box's opencode to reach the network service.

---

## 3. What to do with the tools

Once connected, just describe it in natural language to the agent:

- **Store:** *"Save this into the second brain: <text>"* →
  `knowledge_ingest` with `{"text": "...", "source": "..."}`.
- **Store from URL/YouTube:** *"Save
  <https://…youtube…> to the brain"* → `knowledge_ingest_url`; poll
  `knowledge_job` for completion.
- **Retrieve similar:** *"What do I know about X?"* → `knowledge_search`.
- **Graph lookup:** *"Tell me everything about topic X"* → `knowledge_topic` /
  `knowledge_lookup`.
- **Query:** *"Find all Notes that mention X"* → `knowledge_query` (SPARQL).

Full tool list and semantics: see `src/secondbrain/mcp_server.py` and
`docs/STATUS.md`.

---

## 4. Alternative: stdio over SSH (last resort)

Only needed if the IDE supports **neither** Streamable HTTP nor SSE (i.e. only
stdio MCP servers). Run the MCP server **on the box** through an SSH tunnel:

```json
{
  "mcpServers": {
    "secondbrain": {
      "command": "ssh",
      "args": ["paul@192.168.2.177", "uv run --project ~/second-brain python -m secondbrain.mcp_server"]
    }
  }
}
```
This spawns the stdio server on the box (where the runtime lives at
`127.0.0.1:8000`) and streams the session back over SSH. Requires SSH key auth;
`uv` and the repo live at `~/second-brain` on the box.

> Prefer `/mcp` (Streamable HTTP) over this — it's simpler and needs no SSH key
> setup. Do **not** run stdio pointing at a remote `SECONDBRAIN_RUNTIME_API`
> unless that runtime is reachable from where the stdio process runs (it
> proxies to `SECONDBRAIN_RUNTIME_API`, default `http://127.0.0.1:8000`).

---

## 5. Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `curl :8130/health` fails | `secondbrain-sse.service` not running → `systemctl --user start secondbrain-sse` |
| Reaches port but IDE says "not enabled" | Client lacks permissions/firewall → allow 8130 through the box firewall |
| Handshake fails on `/mcp` | Client speaks only legacy SSE → switch to `/sse` URL |
| `/sse` fails but `/mcp` works (or vice-versa) | Use the transport your client supports: `/mcp` = Streamable HTTP, `/sse` = legacy |
| Tools connect but `/ingest` returns 422 | Body must be `{"text": "...", "source": "..."}` — `text` is required |
| Slow / times out on `/research` or `/ingest_url` | These are async jobs; use `knowledge_ingest_url` + `knowledge_job` and poll, don't block |
| Entity URI not found in lookup | URIs contain `#`/`://` — percent-encode, e.g. `ex%3ANote` |

---

## 6. Security note (open LAN endpoint)

Right now anyone on the LAN can write to your graph. Options:

- **Easiest:** put a shared token in front of the MCP server / API (nginx
  `auth_request` or a header check) so only authorized clients connect.
- **Configure `SECONDBRAIN_API_KEY`** if you add auth to the runtime.
- **Don't expose past your trusted LAN.** The runtime is bound to `0.0.0.0`
  by design so LAN consumers work; don't port-forward it to the internet.

---

## 7. (Implemented) Streamable-HTTP transport

The 8130 service now serves **both** transports from one process: **Streamable
HTTP** at `/mcp` (default, modern) and **legacy SSE** at `/sse` (LibreChat and
older clients). No further work needed unless a future client requires a raw
`/messages`-style transport — see `src/secondbrain/sse_server.py`.
