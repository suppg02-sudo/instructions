# urls — Web server status and URL listing

> **Trigger**: `urls` | **Purpose**: Check which web servers are running, flag any expected-but-down, and list the URLs.
> **When to use**: When the user types `urls` on its own and wants a quick rundown of available web endpoints on this box.

---

## How It Works

When the user types this trigger, follow the phases below.

The hostname of this box is `vm`, so every URL uses the base `http://vm` followed
by the service's port. Output URLs as **clickable markdown links**.

---

### Phase 0 — Known services registry

Check against this known set of expected web services (name → port → path):

| Service | Port | URL |
|---------|------|-----|
| Second Brain runtime (API) | 8000 | `http://vm:8000` |
| Second Brain SSE stream | 8130 | `http://vm:8130` |
| SearXNG search | 8080 | `http://vm:8080` |
| LibreChat | 3080 | `http://vm:3080` |
| LibreChat Admin Panel | 3000 | `http://vm:3000` |
| LiteLLM proxy | 4000 | `http://vm:4000` |
| OpenCode server | 4096 | `http://vm:4096` |
| Service Dashboard | 8090 | `http://vm:8090` |
| Browser terminal (ttyd) | 7681 | `http://vm:7681` |

> If the hostname ever changes (`.bashrc`, `/etc/hostname`), read `hostname` and
> rebuild the base prefix instead of hard-coding `vm`.

### Phase 1 — Detect what is actually listening

- Run `ss -tlnp` (or `netstat -tlnp`) to list listening ports.
- Cross-reference each service's port against the listening set. Also optionally
  `curl -s -o /dev/null -w '%{http_code}' http://vm:<port>` per running service
  to confirm it actually responds.

### Phase 2 — List running URLs

For every service whose port is listening, print a clickable link:

```
- [Second Brain API](http://vm:8000)
- [LibreChat](http://vm:3080)
```

Optionally append the HTTP status code if you probed it.

### Phase 3 — Flag expected-but-down

For every service in the registry whose port is NOT listening, list it as **down**
with the intended URL so the user knows what is missing:

```
- ⚠️ SearXNG — DOWN (expected at http://vm:8080)
```

---

## Output shape

Return a short grouped summary:

1. **Running** — links to each live service.
2. **Down** — expected services that are not listening, with their intended URLs.
3. If everything is up, say so and note the count.
