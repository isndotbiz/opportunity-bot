# Retired MCP Exports
Exported 2026-02-28 per MCP retirement decision (see infrastructure repo: docs/sessions/2026-02-27-mcp-retirement-rag-vs-compound.md).
## What was retired
- **serena MCP** ΓÇö Language server protocol integration. Config preserved in `serena-project-config.yml`.
- **git MCP** ΓÇö @cyanheads/git-mcp-server. Config preserved in `git-mcp-config.json`. Replaced by native `git` CLI commands.
- **local-agents** ΓÇö SSH tunnel to Xeon Qwen3-30B ReAct agents. Config preserved in `retired-mcp-servers.json`.
- **rag-knowledge-base** ΓÇö SSH tunnel to Xeon RAG system. Config preserved in `retired-mcp-servers.json`.
## What remains active
- **context7** ΓÇö Library documentation lookup (stays in `.mcp.json`)
## Why
RAG + compound engineering workflows replace MCP for:
- Factual history ΓåÆ RAG layer (pgvector, ollama embeddings)
- Execution discipline ΓåÆ compound workflows (agents, commands, skills)
