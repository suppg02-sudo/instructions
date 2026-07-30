# Instructions Repository

A collection of **16 mandatory trigger commands** — word-activated command protocols that enable quick, consistent agent behavior.

## What's Inside

This repository contains trigger instructions adapted from the [Pauly project](https://github.com/suppg02-sudo/pauly) — a Directus + Astro Starlight documentation platform.

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/suppg02-sudo/instructions.git
cd instructions

# Install triggers
bash optional/03-triggers/scripts/install.sh

# Verify installation
bash optional/03-triggers/scripts/install.sh --verify
```

### Available Triggers

| Trigger | Command(s) | Purpose |
|---------|------------|---------|
| **Continue** | `co` | Resume most recent task with full context recovery |
| **What Next** | `?`, `what next`, `wn` | Analyse state, surface priorities, recommend next step |
| **Update** | `u`, `update` | Review session work, propose skill/context updates |
| **Improve** | `improve` | Improve ANY component — skills, prompts, menus, config |
| **Brainstorm** | `bs`, `brainstorm` | Quick ideation or structured design sessions |
| **Session** | `session` | Session recovery after compaction — diagnose and fix |
| **Deferred** | `d`, `deferred` | Parked task management — review, resume, archive |
| **Flow** | `flow` | Execution tracing and analysis |
| **Smooth** | `smooth` | Polish rough edges in workflows |
| **Guardian** | `g`, `guardian` | System health menu — status, report, improvements |
| **NextExplorer** | `nx`, `next-explorer` | Redisplay recent session files as clickable links |
| **Menu** | `menu` | Central menu hub for all options and skills |
| **Visual Companion** | `vc`, `visual-companion` | Browser-based diagram generation |
| **Cron** | `cron` | View, edit, monitor scheduled tasks |
| **Space** | `space`, `sp` | Disk space analysis and cleanup |
| **SVG** | `svg`, `diagram` | Publication-ready SVG diagrams from natural language |

## Repository Structure

```
instructions/
├── AGENTS.md                        ← Agent behavioral rules and trigger commands
├── README.md                        ← This file
│
└── optional/
    └── 03-triggers/                 ← Word-activated command protocols
        ├── SKILL.md                 ← Trigger skill documentation
        ├── scripts/
        │   └── install.sh           ← Installation script
        └── templates/
            ├── trigger-words.md     ← Master trigger registry
            └── [16 trigger files]   ← Individual trigger protocols
```

## How Triggers Work

1. **Type a trigger word** (e.g., `co`, `?`, `u`)
2. **Agent recognizes the trigger** and loads the corresponding protocol
3. **Protocol executes** with a structured workflow
4. **Consistent behavior** across sessions

## Documentation

- [AGENTS.md](AGENTS.md) — Agent behavioral rules and trigger commands
- [SKILL.md](optional/03-triggers/SKILL.md) — Detailed trigger skill documentation
- [trigger-words.md](optional/03-triggers/templates/trigger-words.md) — Master trigger registry

## Source

This trigger system is adapted from the [Pauly project](https://github.com/suppg02-sudo/pauly).

## License

MIT
