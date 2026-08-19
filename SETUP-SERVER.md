# Server Setup — Quickstart

Short instructions to bring a new server into the device mesh. Run in order.

## 1. Join the topology mesh (single command)

```bash
git clone https://github.com/suppg02-sudo/topology ~/topology
bash ~/topology/scripts/install.sh --first-flight <hostname>
```

This does everything:
- Installs topology skill + CLI + agent-check skill
- Registers topology in global AGENTS.md
- Scaffolds `devices/<hostname>/` with intent/behaviour/contract from templates
- Commits + pushes to topology repo
- **Auto-installs all 20 triggers** from instructions repo (if cloned)

## 2. Install agent triggers (optional, if not auto-installed)

```bash
git clone https://github.com/suppg02-sudo/instructions ~/instructions
cd ~/instructions
bash optional/03-triggers/scripts/install.sh
bash optional/03-triggers/scripts/install.sh --verify
```

## 3. Wire up MCP servers (optional)

See `mcpinstall.md` for the general MCP setup, or the per-host guides:

- `ubuntu4agentwikimcp.md` — agent-wiki MCP (knowledge store)
- `ubuntu4agentruntimemcp.md` — agent-runtime MCP (rules/skills/context)
- `vm-mcp-skills.md` — vm MCP skills
