# Server Setup — Quickstart

Short instructions to bring a new server into the device mesh. Run in order.

## 1. Join the topology mesh

```bash
git clone https://github.com/suppg02-sudo/topology ~/topology
bash ~/topology/scripts/install.sh          # skill + CLI + registers in global AGENTS.md
bash ~/topology/scripts/install.sh --verify # confirm
```

Then add your box to the shared map and publish:

```bash
cd ~/topology
topology pull
topology update --add <hostname>           # creates your ## device: stanza
topology push -m "topology: add <hostname>"
```

## 2. Install agent triggers (16 mandatory commands)

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
