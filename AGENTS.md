# AGENTS.md — opportunity-research-bot

AI-powered business opportunity discovery. Scrapes Reddit/Indie Hackers/Google, analyzes with local LLM, stores in ChromaDB for semantic search.

## Working Agreement

- Read `CLAUDE.md` before major edits
- No mock/placeholder data in production paths
- Minimal diffs by default
- Run tests after changes
- Commit + sync after verified changes

## Environment

- Windows path: `D:/workspace/projects/opportunity-research-bot`
- Git Bash path: `/d/workspace/projects/opportunity-research-bot`
- Primary branch: `main`

## Key Services

| Service | Endpoint | Notes |
|---------|----------|-------|
| LLM (analysis) | http://100.65.249.20:8200/v1 | Qwen3-30B-A3B, 32K ctx |
| ChromaDB | local | Vector storage for opportunities |
| RAG API | http://100.65.249.20:8400 | Workspace-wide search |

## MCP Servers Available

- **rag-knowledge-base**: SSH to xeon, semantic search over private docs (port 8301)
- **local-agents**: SSH to xeon, ReAct agents via Qwen3-30B-A3B (port 8300)
- **context7**: Up-to-date library docs
- **git**: Git operations

## Coding Agents

- **codex**: Primary (OpenAI subscription, $200/mo)
- **opencode**: Local free via TabbyAPI on xeon (http://100.65.249.20:8200/v1)

## TabbyAPI (Local GPU)

Endpoint: `http://100.65.249.20:8200/v1`
Model: Qwen3-30B-A3B-exl3-3.0bpw (32K context, free)
Use opencode to run tasks against local GPU.

## Standard Workflow

1. `git status --short --branch`
2. Implement smallest safe change
3. Run targeted tests
4. Review diff: `git diff --stat && git diff`
5. Commit with clear message
6. Push to origin/main

## Anti-Patterns

- Do not hardcode API keys or credentials
- Do not scrape without rate limiting
- Do not leave ChromaDB in inconsistent state
- Do not force-push `main`

## Quick Ops

```bash
# Git
git status --short --branch
git add <files>
git commit -m "<message>"
git push origin main

# Run pipeline
python production_opportunity_pipeline.py

# Search opportunities
python -c "import chromadb; ..."
```

---

If uncertain: **smallest safe fix + explicit verification**.
