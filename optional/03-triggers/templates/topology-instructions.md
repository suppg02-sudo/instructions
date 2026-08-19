# topology — Device Mesh Alignment & Management

> **Trigger**: `topology` | **Purpose**: Align this device with central topology, then manage device mesh
> **Context file**: this file
> **When to use**: When the user types `topology` — auto-aligns with central topology, then shows management menu via question tool

## Agent Workflow

When user types `topology`, YOU (the agent) MUST:

1. **Run alignment** — execute `topology align --auto` via bash tool
2. **Present menu** — use `question` tool to show management options
3. **Execute selection** — run chosen topology subcommand via bash tool

## Step 1: Auto-Align (bash tool)

```bash
topology align --auto
```

This pulls latest, detects drift, runs converge, validates contract peers.

## Step 2: Present Menu (question tool)

After alignment completes, use the **question tool** with these options:

```json
{
  "question": "Topology aligned ✓ — choose action:",
  "header": "Topology Menu",
  "options": [
    {"label": "Show status", "description": "topology status — repo state, device count, dirty?"},
    {"label": "List devices", "description": "topology list — all devices + roles"},
    {"label": "Show this device", "description": "topology show — this device's full stanza"},
    {"label": "Show all devices", "description": "topology show (no args) — all stanzas"},
    {"label": "Sync (pull+push)", "description": "topology sync — pull, commit diff, push"},
    {"label": "Probe reachability", "description": "topology probe --write --push — refresh reachability"},
    {"label": "Check health", "description": "topology check — mesh, peers, secrets validation"},
    {"label": "Converge templates", "description": "topology converge — reconcile all devices to templates"},
    {"label": "Edit this device", "description": "topology update — edit this device's stanza"},
    {"label": "Exit", "description": "Alignment complete, ready to work"}
  ],
  "multiple": false
}
```

## Step 3: Execute Selection (bash tool)

Based on question tool response, run the corresponding command:

| Selection | Command |
|-----------|---------|
| Show status | `topology status` |
| List devices | `topology list` |
| Show this device | `topology show` |
| Show all devices | `topology show` (no args) |
| Sync (pull+push) | `topology sync` |
| Probe reachability | `topology probe --write --push` |
| Check health | `topology check` |
| Converge templates | `topology converge` |
| Edit this device | `topology update --add <name>` / `topology update --remove <name>` |
| Exit | (do nothing) |

## Alignment Phase (automatic)

`topology align --auto` does:
- Pulls latest topology from central repo
- Checks this device's stanza in TOPOLOGY.md
- Verifies per-device files (intent, behaviour, contract, triggers, topology)
- Validates contract peer symmetry
- Auto-reconciles via converge if needed

## Example Flow

```
> topology
[align] Pulling latest topology...
[align] Central stanza found for ubuntu4
[align] Per-device files: contract.md ✗, triggers.md ✗
[align] Running converge...
  scaffolded ubuntu4/contract.md, ubuntu4/triggers.md
  installed 20 triggers
[align] Alignment complete

🧭 Topology Menu — ubuntu4 aligned ✓

[question tool presents 10 options]
User selects "Show status"
> topology status
repo: /home/paul/topology  branch: main
devices: 5
dirty: no
```