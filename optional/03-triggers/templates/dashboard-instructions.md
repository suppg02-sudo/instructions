# dashboard — Add a new icon to the service dashboard linked to a URL

> **Trigger**: `>d`, `>dash`, `>dashboard` | **Purpose**: Add a new icon/card to the service dashboard and associate it with a URL link
> **When to use**: User types `>d`, `>dash`, or `>dashboard` to add a service to the dashboard

---

## How It Works

When the user types this trigger, add a new card to the service dashboard
(`~/dashboard/index.html`) linked to a URL.

---

### Phase 0 — Determine the service and URL

Use the **recent session content** to infer what service the user wants to add
and what URL it should link to (e.g. a web server discussed or started
earlier in the session).

- If it is **obvious** from recent session context (a service/port/URL was
  clearly discussed), do NOT ask — proceed with the inferred values.
- If it is **not clear** what service to add or what URL to link, ask the user
  via the **question tool** (heading, name/desc, URL, icon) before proceeding.
- The current dashboard lives at `~/dashboard/index.html` and is served at
  `http://vm:8090`, so `http://vm` links are the norm; APIs/MCP endpoints are
  intentionally excluded unless the user wants one.

### Phase 1 — Add the card

Append an entry to the `services = [...]` array in the `<script>` block of
`~/dashboard/index.html`:

```js
{
  name: "Service Name",
  desc: "Short description",
  url: "http://vm:PORT",
  icon: '<svg viewBox="0 0 24 24" ...>...</svg>'
}
```

- Match the existing style of the current cards.
- Reuse an existing icon where possible, or provide a simple inline SVG.

### Phase 2 — Verify

1. Confirm the new entry is present in `services`.
2. Restart the dashboard service to pick up the change:
   `systemctl --user restart dashboard`
3. Confirm it is up: `systemctl --user status dashboard` (serving :8090).

### Phase 3 — Report

Tell the user what was added, the URL it links to, and confirm the dashboard
was restarted (`http://vm:8090`).
