# topology — Device Mesh Alignment & Management

> **Trigger**: `topology` | **Purpose**: Align this device with central topology, then manage device mesh
> **Context file**: this file
> **When to use**: When the user types `topology` — auto-aligns with central topology, then shows management menu

## What `topology` does

1. **Auto-align** — runs `topology align --auto` to sync with central topology
2. **Show menu** — presents topology management options via question tool

## Alignment Phase (automatic)

Runs `topology align --auto` which:
- Pulls latest topology from central repo
- Checks this device's stanza in TOPOLOGY.md
- Verifies per-device files (intent, behaviour, contract, triggers, topology)
- Validates contract peer symmetry
- Auto-reconciles via converge if needed

## Management Menu (after alignment)

Presents options via question tool:

| Option | Action |
|--------|--------|
| **Show status** | `topology status` — repo state, device count, dirty? |
| **List devices** | `topology list` — all devices + roles |
| **Show this device** | `topology show` — this device's full stanza |
| **Show all devices** | `topology show` (no args) — all stanzas |
| **Sync (pull+push)** | `topology sync` — pull, commit diff, push |
| **Probe reachability** | `topology probe --write --push` — refresh reachability |
| **Check health** | `topology check` — mesh, peers, secrets validation |
| **Converge templates** | `topology converge` — reconcile all devices to templates |
| **Edit this device** | `topology update` — edit this device's stanza |
| **Aligned & done** | Exit — alignment complete, ready to work |

## Implementation

```bash
# 1. Auto-align (non-interactive)
topology align --auto

# 2. Show menu via question tool
# Options presented via question tool
# Execute selected topology subcommand
```

## Example Flow

```
> topology
[align] Pulling latest topology...
[align] Central stanza found for ubuntu4
[align] Per-device files: intent.md ✓, behaviour.md ✓, contract.md ✗, triggers.md ✗
[align] Contract declares 1 peer(s)
[align] Running converge...
  scaffolded ubuntu4/contract.md, ubuntu4/triggers.md
  installed 20 triggers
[align] Alignment complete

🧭 Topology Menu — ubuntu4 aligned ✓

1. Show status
2. List devices  
3. Show this device
4. Show all devices
5. Sync (pull+push)
6. Probe reachability
7. Check health
8. Converge templates
9. Edit this device
10. Aligned & done (Exit)

Select [1-10]:
```

## Files Created on First Alignment

- `devices/<hostname>/contract.md` — from global template
- `devices/<hostname>/triggers.md` — per-device trigger extras
- `~/.config/opencode/agents/context/` — all 20 trigger context files