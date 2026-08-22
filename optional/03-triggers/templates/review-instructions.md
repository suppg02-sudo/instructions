# review — Session Log Review & Improvement

> **Trigger**: `review` (or `r`) | **Purpose**: Review opencode session logs for corrections, deviations, repeating errors, and improvements
> **Context file**: this file
> **When to use**: When the user types `review` (or `r`) to analyze session logs for improvements

---

## Agent Workflow

When user types `review` (or `r`), YOU (the agent) MUST:

1. **Ask scope** — use question tool to determine review scope
2. **Analyze logs** — read and analyze session logs for the specified period
3. **Report findings** — present findings with corrections, deviations, repeating errors
4. **Propose fixes** — suggest corrections, trigger suggestions for repeated tasks
5. **Execute fixes** — apply approved fixes

---

## Step 1: Determine Scope (question tool)

```json
{
  "question": "Review session logs — what scope?",
  "header": "Review Scope",
  "options": [
    {"label": "Current session only (Recommended)", "description": "Review just this session's logs"},
    {"label": "Last 1 day", "description": "Review logs from the last 24 hours"},
    {"label": "Last 3 days", "description": "Review logs from the last 72 hours"},
    {"label": "Last 7 days", "description": "Review logs from the last week"},
    {"label": "Custom range", "description": "Specify custom date range"}
  ],
  "multiple": false
}
```

If "Custom range" selected, ask for start/end dates via follow-up question.

---

## Step 2: Analyze Session Logs

Read session logs from `~/.config/opencode/logs/` (or wherever logs are stored):

```bash
# Find log files for the scope
find ~/.config/opencode/logs -name "*.jsonl" -mtime -${DAYS} | head -20

# Or read current session log
cat ~/.config/opencode/logs/session-$(date +%Y-%m-%d).jsonl
```

**Analyze for:**

| Category | What to Look For |
|----------|------------------|
| **Repeating errors** | Same error appearing 2+ times across sessions |
| **Deviations from intent** | Work that drifted from stated goals/instructions |
| **Repeating patterns** | Same manual steps repeated 3+ times (candidate for trigger/skill) |
| **Failed verifications** | Tests/checks that failed but were ignored |
| **Incomplete tasks** | Tasks marked started but not completed/verified |
| **Skill gaps** | Missing skills that would have automated manual work |
| **Trigger opportunities** | Manual sequences repeated 3+ times (candidate for new trigger) |
| **Configuration drift** | Config changes not persisted to repo |

---

## Step 3: Report Findings (question tool)

Present findings grouped by category:

```json
{
  "question": "Review complete. Found ${COUNT} issues. Apply fixes?",
  "header": "Review Results",
  "options": [
    {"label": "Apply all fixes (Recommended)", "description": "Fix all identified issues"},
    {"label": "Select specific fixes", "description": "Choose which fixes to apply"},
    {"label": "Create triggers for repeated tasks", "description": "Generate trigger/skill proposals for repeated patterns"},
    {"label": "View full report", "description": "Show detailed findings before deciding"},
    {"label": "Skip fixes", "description": "Just view report, no changes"}
  ],
  "multiple": false
}
```

If "Select specific fixes" or "View full report", present detailed breakdown.

---

## Step 4: Execute Fixes

For each approved fix category:

### Fix Repeating Errors
- Apply the fix to root cause (not symptoms)
- Add test/verification to prevent regression
- Update relevant skill/trigger if applicable

### Fix Deviations from Intent
- Realign work with original intent/instructions
- Update AGENTS.md / intent.md if intent has evolved
- Document deviation in session log

### Create Triggers for Repeated Tasks
- For each pattern repeated 3+ times:
  - Generate trigger schema via `skill-factory new`
  - Install via `skill-factory generate`
  - Register in `trigger-words.md`

### Fix Configuration Drift
- Persist config changes to repo (AGENTS.md, intent.md, triggers.yaml)
- Update `.env` templates if needed

### Address Skill Gaps
- Propose new skill via `skill-factory new`
- Add to instructions repo if generic

---

## Step 5: Verification & Report

After fixes applied:

1. Run verification: `opencode agent-check --agent opencode --exit`
2. Update session log with review summary
3. Present summary of changes made

---

## Implementation Notes

### Log Locations
- OpenCode logs: `~/.config/opencode/logs/session-*.jsonl`
- Trigger usage: `~/.config/opencode/triggers.yaml`
- Session state: `~/.config/opencode/state/`

### Key Log Fields to Analyze
- `tool_calls` — repeated tool sequences
- `errors` — error patterns
- `tool_results` — failed operations
- `user_inputs` — repeated manual steps

### Trigger Suggestion Heuristics
| Pattern | Threshold | Action |
|---------|-----------|--------|
| Same tool sequence | 3+ times | Create trigger |
| Same error | 2+ times | Fix root cause |
| Same manual edit | 3+ times | Create skill/trigger |
| Same config change | 2+ times | Persist to repo |

---

## Example Output

```
📊 Review: Last 3 days (47 log entries)

🔴 Repeating Errors (3):
  1. "Permission denied" on ssh to ubuntu4 — 4 occurrences
     → Fix: SSH key setup (already done)
  2. "Permission denied" on git push — 2 occurrences  
     → Fix: Git credentials / SSH key for GitHub
  3. "Module not found: react-markdown" — 2 occurrences
     → Fix: Dockerfile missing shared package install

🟡 Deviations (2):
  1. Skill factory schema changed but templates not updated
  2. Contract entries added but not merged to device contract.md

🔵 Trigger Opportunities (4):
  1. SSH key setup sequence — 4 times → trigger: ssh-setup
  2. Docker rebuild sequence — 3 times → trigger: docker-rebuild
  3. Git commit/push sequence — 5 times → trigger: git-sync
  4. Skill generation sequence — 3 times → trigger: skill-gen

🟢 Suggested Actions:
  [ ] Fix SSH/GPG key setup (DONE)
  [ ] Update Dockerfiles for shared packages
  [ ] Create 4 new triggers
  [ ] Merge contract entries to device contracts
  [ ] Update skill-factory templates
```

---

## Files
- Context: `~/.config/opencode/agents/context/review-instructions.md`
- Trigger: `review`, `r` (added to trigger-words.md)
- Log analysis script: `~/.config/opencode/scripts/review_logs.py` (optional)
