# AGENTS.md — Instructions Repository

> **Point your IDE at this repo.** This file tells the agent everything it needs to know about the trigger commands and behavioral rules.

## What This Repo Does

This repository contains **16 mandatory trigger commands** — word-activated command protocols that enable quick, consistent agent behavior. Each trigger is a short word (e.g., `?`, `co`, `u`) that activates a predefined workflow.

## Quick Start

**Installation**:
```bash
bash optional/03-triggers/scripts/install.sh
```

**Verify installation**:
```bash
bash optional/03-triggers/scripts/install.sh --verify
```

## Trigger Commands

| Trigger | Command(s) | Purpose | Category |
|---------|------------|---------|----------|
| **Continue** | `co` | Resume most recent task with full context recovery | Core Workflow |
| **What Next** | `?`, `what next`, `wn` | Analyse state, surface priorities, recommend next step | Core Workflow |
| **Update** | `u`, `update` | Review session work, propose skill/context updates | Self-Improvement |
| **Improve** | `improve` | Improve ANY component — skills, prompts, menus, config | Self-Improvement |
| **Brainstorm** | `bs`, `brainstorm` | Quick ideation or structured design sessions | Creative |
| **Session** | `session` | Session recovery after compaction — diagnose and fix | Reliability |
| **Deferred** | `d`, `deferred` | Parked task management — review, resume, archive | Task Management |
| **Flow** | `flow` | Execution tracing and analysis | Analysis |
| **Smooth** | `smooth` | Polish rough edges in workflows | Analysis |
| **Guardian** | `g`, `guardian` | System health menu — status, report, improvements | Operations |
| **NextExplorer** | `nx`, `next-explorer` | Redisplay recent session files as clickable links | Navigation |
| **Menu** | `menu` | Central menu hub for all options and skills | Navigation |
| **Visual Companion** | `vc`, `visual-companion` | Browser-based diagram generation | Creative |
| **Cron** | `cron` | View, edit, monitor scheduled tasks | Operations |
| **Space** | `space`, `sp` | Disk space analysis and cleanup | Operations |
| **Dashboard** | `>d`, `>dash`, `>dashboard` | Add a new icon to the service dashboard linked to a URL (infer from session; ask only if unclear) | Operations |
| **URLs** | `urls` | Check which web servers are running, list URLs as http://vm links | Operations |
| **SVG** | `svg`, `diagram` | Publication-ready SVG diagrams from natural language | Creative |
| **MCP Install** | `mcpinstall` | Interactive install of the shared MCP servers (vm ⇄ ubuntu4) via question tool, cross-machine by default | Operations |
| **Topology** | `topology` | Device mesh awareness — read/update the shared TOPOLOGY.md (github.com/suppg02-sudo/topology) across all machines, git-synced | Navigation |
 | **Agent Check** | `agent-check`, `check agents` | Universal per-agent health/preflight checklist (opencode, librechat, nao) — static + live layers via `agent-check.py --agent X` (see `skills/agent-check` in the topology repo) | Operations |

## Repo Structure

```
instructions/
├── AGENTS.md                        ← YOU ARE HERE
├── README.md                        ← Human-readable overview
│
└── optional/
    └── 03-triggers/                 ← Word-activated command protocols (17 triggers)
        ├── SKILL.md                 ← Trigger skill documentation
        ├── scripts/
        │   └── install.sh           ← Installation script
        └── templates/
            ├── trigger-words.md     ← Master trigger registry
            ├── continue-instructions.md
            ├── what-next-instructions.md
            ├── update-instructions.md
            ├── improve-instructions.md
            ├── brainstorm-instructions.md
            ├── session-recovery.md
            ├── deferred-options.md
            ├── flow-instructions.md
            ├── smooth-instructions.md
            ├── guardian-instructions.md
            ├── next-explorer-instructions.md
            ├── central-menu.md
            ├── visual-companion-instructions.md
            ├── cron-instructions.md
            ├── space-instructions.md
            ├── dashboard-instructions.md
            └── svg-instructions.md
```

## Behavioral Rules

These rules define how the agent should behave when working on this repo:

### Process
- **Rules first, commands second**: This file defines behavior; command/tool details live in dedicated context files under `optional/03-triggers/templates/`.
- **Load skills first**: Before acting, load every skill that might apply (even 1% chance). Skills define how to approach tasks correctly.
- **Be creative**: Don't just execute — propose better paths if you see one.
- **Context over memory**: Persistent rules belong here, in skills, or in context files. Never rely on session memory for repeatable behavior.
- **Use NextExplorer**: After completing any session task, run the `nx` trigger to display clickable links for modified files.

### Quality
- **Test fixes**: Verify after changes. Don't report done without evidence.
- **Prevent recurrence**: After fixing any issue, proactively suggest improvements to avoid the same or similar issues.
- **No interactive editors**: Never use interactive editors (nano, vim). Use Python, here-docs, or other non-interactive constructs.

### Safety
- **Deletion safety**: Deletions need explicit confirmation, current target verification, and auth check before executing.
- **Dangerous commands**: Run an audit checklist before executing destructive commands (rm -rf, docker system prune, dd, etc.).

### Presentation
- **Menu presentation**: Always use the question tool with clear options. Lead with `(Recommended)`. Always include an exit option. Never hand-craft question JSON.

### Anti-Patterns
- Don't auto-load skills unless triggered by user intent
- Don't use `fetch` when `web_search`/`browser`/`mcp` is available
- Don't ignore local or MCP-available tools in favour of remote alternatives
- Don't use `knowledge_research` (the Second Brain research pipeline) for simple factual look-up queries — it is a heavy search→fetch→summarize→ingest pipeline that writes notes into the knowledge graph. Prefer a plain web search / `webfetch` and answer in chat; reach for `knowledge_research` only when the user wants to persist a topic into the second brain or explicitly asks to research/save it.

## Source

This trigger system is adapted from the [Pauly project](https://github.com/suppg02-sudo/pauly) — a Directus + Astro Starlight documentation platform.
