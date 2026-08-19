# >brain — Save to Second Brain

> **Trigger**: `>brain` | **Purpose**: Ingest current session/topic into the Second Brain knowledge graph
> **Context file**: this file
> **When to use**: When the user types `>brain` to save the current conversation, topic, or findings to the Second Brain.

## What `>brain` does

1. **Review the current session** — identify the main topic, key findings, decisions, and outcomes
2. **Present options** via the question tool:
   - Save entire session summary
   - Save specific topic/finding
   - Save with custom text
   - Cancel
3. **Ingest into Second Brain** using `knowledge_ingest` MCP tool
4. **Confirm** with link to the note in the Second Brain

## Implementation

- Use `knowledge_ingest` MCP tool with the text and source
- Source format: `session:YYYY-MM-DD` or `topic:<topic-name>`
- After ingestion, provide a clickable link to the note

## Example

User types `>brain` after a research session about "edge routers":

1. Agent identifies the topic: "Edge Router Configuration"
2. Agent presents options via question tool
3. User selects "Save entire session summary"
4. Agent calls `knowledge_ingest(text="...", source="session:2026-08-18")`
5. Agent confirms: "Saved to Second Brain: Edge Router Configuration"
