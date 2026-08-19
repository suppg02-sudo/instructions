#!/usr/bin/env python3
"""
Topology CLI — Device mesh awareness with per-node git repo for automated backup.

On enrollment, creates a per-node git repo (GitHub) for backing up:
- AGENTS.md
- intent.md  
- config files
- OKF exports
- state snapshots
"""

import os
import sys
import subprocess
import json
import getpass
from pathlib import Path
from typing import Optional

TOPOLOGY_REPO = os.environ.get("TOPOLOGY_REPO", "https://github.com/suppg02-sudo/topology")
TOPOLOGY_DIR = Path.home() / ".topology"
PER_NODE_REPO_BASE = "https://github.com/suppg02-sudo"  # GitHub org/user


def run(cmd: list[str], cwd: Optional[Path] = None, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    """Run a command."""
    return subprocess.run(cmd, cwd=cwd, check=check, capture_output=capture, text=True)


def get_github_token() -> str:
    """Get GitHub PAT token from user."""
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token.strip()
    
    print("GitHub PAT token required (repo scope) for per-node repo creation.")
    print("Token will not be echoed.")
    token = getpass.getpass("GitHub PAT: ").strip()
    if not token:
        sys.exit("No token provided")
    return token


def github_api(token: str, method: str, endpoint: str, data: dict = None) -> dict:
    """Make GitHub API call."""
    import urllib.request
    import urllib.error
    
    url = f"https://api.github.com{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    
    req_data = None
    if data:
        req_data = json.dumps(data).encode()
    
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        sys.exit(f"GitHub API error ({e.code}): {error_body}")


def create_per_node_repo(token: str, hostname: str) -> str:
    """Create a per-node repo on GitHub."""
    repo_name = f"secondbrain-{hostname.replace('.', '-')}"
    
    # Check if repo exists
    try:
        github_api(token, "GET", f"/repos/suppg02-sudo/{repo_name}")
        print(f"Repo already exists: {repo_name}")
        return f"{PER_NODE_REPO_BASE}/{repo_name}.git"
    except SystemExit:
        pass  # Not found, will create
    
    # Create repo
    print(f"Creating per-node repo: {repo_name}")
    result = github_api(token, "POST", "/user/repos", {
        "name": repo_name,
        "description": f"Second Brain backup for {hostname} — AGENTS.md, intent.md, config, OKF exports",
        "private": True,
        "auto_init": True,
    })
    
    clone_url = result["clone_url"]
    print(f"Created: {clone_url}")
    return clone_url.replace("https://github.com/", "https://github.com/")  # Use HTTPS


def clone_or_update_repo(repo_url: str, target_dir: Path, token: str) -> None:
    """Clone or update a git repo with token auth."""
    auth_url = repo_url.replace("https://github.com/", f"https://{token}@github.com/")
    
    if target_dir.exists():
        print(f"Updating {target_dir}")
        run(["git", "-C", str(target_dir), "pull", "--rebase", auth_url])
    else:
        print(f"Cloning to {target_dir}")
        run(["git", "clone", auth_url, str(target_dir)])


def setup_per_node_repo(hostname: str) -> Path:
    """Set up per-node backup repo."""
    token = get_github_token()
    repo_url = create_per_node_repo(token, hostname)
    
    repo_dir = Path.home() / f".secondbrain-backup-{hostname.replace('.', '-')}"
    clone_or_update_repo(repo_url, repo_dir, token)
    
    # Create initial backup structure
    (repo_dir / "config").mkdir(exist_ok=True)
    (repo_dir / "state").mkdir(exist_ok=True)
    (repo_dir / "okf-exports").mkdir(exist_ok=True)
    
    # Add README
    readme = repo_dir / "README.md"
    if not readme.exists():
        readme.write_text(f"""# Second Brain Backup — {hostname}

Automated backup repository for `{hostname}` Second Brain node.

## Contents

- `config/` — AGENTS.md, intent.md, opencode.jsonc, .env (secrets excluded)
- `state/` — current_state.md, deferred_options.json, trigger state
- `okf-exports/` — Periodic OKF knowledge graph exports

## Sync

Run `topology backup` to push latest state.
""")
        run(["git", "-C", str(repo_dir), "add", "."])
        run(["git", "-C", str(repo_dir), "commit", "-m", f"init: backup structure for {hostname}"])
        run(["git", "-C", str(repo_dir), "push"])
    
    return repo_dir


def enroll() -> None:
    """Enroll this device in the topology mesh."""
    import socket
    hostname = socket.gethostname()
    
    print(f"=== Topology Enrollment: {hostname} ===")
    
    # Get token upfront for both repos
    token = get_github_token()
    
    # 1. Clone shared topology repo
    if not TOPOLOGY_DIR.exists():
        print(f"Cloning shared topology repo: {TOPOLOGY_REPO}")
        auth_topo_url = TOPOLOGY_REPO.replace("https://github.com/", f"https://{token}@github.com/")
        run(["git", "clone", auth_topo_url, str(TOPOLOGY_DIR)])
    else:
        run(["git", "-C", str(TOPOLOGY_DIR), "pull", "--rebase"])
    
    # 2. Create per-node backup repo
    backup_dir = setup_per_node_repo(hostname)
    print(f"Per-node backup repo: {backup_dir}")
    
    # 3. Add this device to TOPOLOGY.md (interactive)
    topo_file = TOPOLOGY_DIR / "TOPOLOGY.md"
    print(f"\nEdit {topo_file} to add this device's stanza.")
    print("Run `topology update --add {hostname}` after editing.")
    
    print("\n✓ Enrollment complete. Next steps:")
    print(f"  1. Edit {topo_file} to add your device stanza")
    print(f"  2. Run: topology push -m 'topology: add {hostname}'")
    print(f"  3. Run: topology backup  # to push initial config to {backup_dir}")


def backup() -> None:
    """Push current config/state to per-node backup repo."""
    import socket
    hostname = socket.gethostname()
    backup_dir = Path.home() / f".secondbrain-backup-{hostname.replace('.', '-')}"
    
    if not backup_dir.exists():
        sys.exit("Per-node backup repo not found. Run `topology enroll` first.")
    
    # Files to backup (exclude secrets)
    config_files = [
        ("~/.config/opencode/AGENTS.md", "config/AGENTS.md"),
        ("~/second-brain/intent.md", "config/intent.md"),
        ("~/.config/opencode/opencode.jsonc", "config/opencode.jsonc"),
        ("~/.config/opencode/triggers.yaml", "config/triggers.yaml"),
        ("~/.config/opencode/current_state.md", "state/current_state.md"),
        ("~/.config/opencode/deferred_options.json", "state/deferred_options.json"),
    ]
    
    for src, dst in config_files:
        src_path = Path(src).expanduser()
        if src_path.exists():
            dst_path = backup_dir / dst
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            dst_path.write_text(src_path.read_text())
    
    # OKF exports
    okf_dir = backup_dir / "okf-exports"
    okf_dir.mkdir(exist_ok=True)
    
    # Check for OKF exports in second-brain
    sb_okf = Path("~/second-brain/okf-exports").expanduser()
    if sb_okf.exists():
        for f in sb_okf.glob("*.md"):
            (okf_dir / f.name).write_text(f.read_text())
    
    # Commit and push
    run(["git", "-C", str(backup_dir), "add", "."])
    try:
        run(["git", "-C", str(backup_dir), "commit", "-m", f"backup: {hostname} $(date -Iseconds)"])
        run(["git", "-C", str(backup_dir), "push"])
        print(f"✓ Backup pushed to {backup_dir}")
    except subprocess.CalledProcessError:
        print("No changes to commit")


def status() -> None:
    """Show topology status."""
    import socket
    hostname = socket.gethostname()
    
    print("=== Topology Status ===")
    print(f"Hostname: {hostname}")
    print(f"Shared topology: {TOPOLOGY_DIR}")
    if TOPOLOGY_DIR.exists():
        run(["git", "-C", str(TOPOLOGY_DIR), "status", "--short"])
    else:
        print("  (not cloned)")
    
    backup_dir = Path.home() / f".secondbrain-backup-{hostname.replace('.', '-')}"
    print(f"Per-node backup: {backup_dir}")
    if backup_dir.exists():
        run(["git", "-C", str(backup_dir), "status", "--short"])
    else:
        print("  (not initialized)")


def main():
    if len(sys.argv) < 2:
        print("Usage: topology <enroll|backup|status>")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "enroll":
        enroll()
    elif cmd == "backup":
        backup()
    elif cmd == "status":
        status()
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: topology <enroll|backup|status>")
        sys.exit(1)


if __name__ == "__main__":
    main()