# Remote MCP Client — Connect Another IDE to the Second Brain

> How to connect an IDE/agent on **another LAN PC** (Cursor, W&B, VSCode via
> Cline/Roo, Windsurf, another opencode, LibreChat, etc.) to this box's Second
> Brain knowledge runtime for **storing** and **retrieving** knowledge.

**Box (this machine):** LAN IP `192.168.2.177` · hostname `vm`

**Recommended path:** use the **already-running SSE MCP server**. It proxies to
the runtime API *on this box*, so the remote client needs **no code, no
packages, no repo checkout** — just point its MCP client at one SSE URL.

---

## 0. Prerequisites / reachability

- Make sure you can reach the box from the other PC:
  ```bash
  curl -s http://192.168.2.177:8000/health    # runtime API   → {"status":"ok"}
  curl -s http://192.168.2.177:8130/health    # MCP over SSE  → {"status":"ok","transport":"sse",...}
  ```
- The MCP SSE service is already running as a systemd **user** unit on the box:
  `secondbrain-sse.service` (port 8130, binding `0.0.0.0`).
- **No auth token** is currently required. The LAN endpoint is open. If the LAN
  is trusted (home network) this is fine; see §6 to lock it down if not.

---

## 1. The single URL to give your IDE

```
http://192.168.2.177:8130/sse
```

Transport type: **SSE** (legacy Server-Sent Events transport, `mcp 2.0`).
Tools exposed: `knowledge_ingest`, `knowledge_search`, `knowledge_lookup`,
`knowledge_query`, `knowledge_topic`, `knowledge_ingest_url`,
`knowledge_job`, `knowledge_export`, `knowledge_import`, `knowledge_enrich`,
`knowledge_consolidate`, `knowledge_prune`, `knowledge_reindex`,
`knowledge_delete_note`, `knowledge_topic_curate`, `knowledge_research`.

---

## 2. Registering it in common IDEs

### Cursor
`Cursor Settings → MCP → Add new MCP server` →
- **Type:** SSE
- **Name:** `secondbrain` (or whatever)
- **URL:** `http://192.168.2.177:8130/sse`
Save. Cursor lists the `knowledge_*` tools (look for a green "connected").
Cursor needs to run with an agent model to invoke the tools.

### Windsurf
`Settings → MCP Servers → +` → choose **SSE** → enter the URL above.

### VSCode + Cline / Roo Code (or vscode-mcp)
In the *mcp.json* / `~/.vscode/mcp.json` of the other machine:
```json
{
  "mcpServers": {
    "secondbrain": {
      "type": "http",
      "url": "http://192.168.2.177:8130/sse"
    }
  }
}
```
> Note: some of these clients only speak the newer **Streamable HTTP**
> transport. If Cline/Roo/VSCode reports a handshake failure, register the
> server as stdio over SSH instead (§4), or add a Streamable-HTTP front on the
> box (§7).

### LibreChat (self-hosted web) / other SSE-capable clients on the LAN
Register an **MCP server of type `sse`** pointing at the same URL.

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

## 4. Alternative: stdio over SSH (if your IDE can't speak SSE)

If the IDE only supports stdio MCP servers, run the MCP server **on the other
machine** through an SSH tunnel to the box's API:

1. On the **box**, expose the runtime API port already does this (`0.0.0.0:8000`).
2. In the remote IDE's MCP config, use a stdio command that tunnels over SSH:
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
   `127.0.0.1:8000`) and streams the session back over SSH. Requires SSH
   key auth; `uv` and the repo live at `~/second-brain` on the box.

> Do **not** use stdio pointing at a remote `SECONDBRAIN_RUNTIME_API` unless
> that runtime is reachable from wherever the stdio process runs; the stdio
> server proxies to `SECONDBRAIN_RUNTIME_API` (default `http://127.0.0.1:8000`).

---

## 5. Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `curl :8130/health` fails | `secondbrain-sse.service` not running → `systemctl --user start secondbrain-sse` |
| Reaches port but IDE says "not enabled" | Client lacks permissions/firewall → allow 8130 through the box firewall |
| Handshake fails on newer clients | Client wants Streamable HTTP, not legacy SSE → use §4 (stdio/SSH) or §7 |
| Tools connect but `/ingest` returns 422 | Body must be `{"text": "...", "source": "..."}` — `text` is required |
| Slow / times out on `/research` or `/ingest_url` | These are async jobs; use `knowledge_ingest_url` + `knowledge_job` and poll, don't block |
| Entity URI not found in lookup | URIs contain `#`/`://` — percent-encode, e.g. `ex%3ANote` |

---

## 6. Security note (open LAN endpoint)

Right now anyone on the LAN can write to your graph. Options:

- **Easiest:** put a shared token in front of the SSE server / API (nginx
  `auth_request` or a header check) so only authorized clients connect.
- **Configure `SECONDBRAIN_API_KEY`** if you add auth to the runtime.
- **Don't expose past your trusted LAN.** The runtime is bound to `0.0.0.0`
  by design so LAN consumers work; don't port-forward it to the internet.

---

## 7. (Future / optional) Streamable-HTTP transport

The current service exposes legacy **SSE**. The MCP ecosystem is moving to
**Streamable HTTP** (`sse` + POST endpoints under one URL). If a client
requires it, add a Streamable-HTTP front to `src/secondbrain/` (Starlette
`StreamableHTTPServerTransport` is available in `mcp`), then point clients at
`http://192.168.2.177:8130/mcp`. Track in `docs/ROADMAP.md`.
