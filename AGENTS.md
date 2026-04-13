# PROJECT KNOWLEDGE BASE

**Generated:** 2026-04-09
**Commit:** 1512cf4
**Branch:** main

## OVERVIEW
AI product research TUI — 8-stage pipeline streaming Claude/Ollama results live in terminal.

## STRUCTURE
```
Prode/
├── main.py          # Textual App, all UI widgets, worker loop
├── researcher.py     # Dual-backend streaming (Anthropic SDK, OpenAI-compat)
├── stages.py        # 8 Stage dataclasses with prompt templates
├── exporter.py       # Markdown file export
├── requirements.txt  # anthropic, openai, textual, python-dotenv
├── .env.example      # ANTHROPIC_API_KEY template
└── README.md
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Add a research stage | `stages.py` | Append a `Stage(...)` to `STAGES` list |
| Change provider logic | `researcher.py` | `_stream_anthropic()` or `_stream_ollama()` |
| Modify UI layout | `main.py` lines 338-407 | `APP_CSS` string |
| Add a widget | `main.py` | New class extending `Widget` or `Container` |
| Change prompts | `stages.py` | Edit `prompt_template` strings |
| Add export format | `exporter.py` | Modify `export_results()` |
| Change keybindings | `main.py` line 416 | `BINDINGS` list |
| Rate-limit handling | `main.py` lines 571-605 | `while True` retry loop in `_run_all_stages` |

## CONVENTIONS
- **No package structure** — flat modules, bare imports (`from stages import STAGES`)
- **Streaming event tuples** — `(event_type, content)` where type is one of: `text`, `searching`, `search_done`, `rate_limit`, `error`
- **TUI framework** — Textual with inline `DEFAULT_CSS` / `DEFAULT_CSS` blocks per widget
- **Provider model** — `ProviderConfig` dataclass branches on `.provider == "anthropic"` vs `"ollama"`
- **Stage names** — use `stage.id` for dict keys, `stage.name` for display, `stage.short_name` for sidebar
- **Error handling** — catch and yield `("error", msg)` tuple; never raise from streaming generators
- **`@work(name="research")`** — the async worker that drives the stage loop; check `self._running` guard before starting

## ANTI-PATTERNS (THIS PROJECT)
- **Don't** add `__init__.py` — project runs as scripts, not a package
- **Don't** use `print()` — all output goes through `self._append_output()` or Textual notifications
- **Don't** import `anthropic` or `openai` at module level in `researcher.py` — they're imported inside the streaming functions so the app starts without them installed if unused
- **Don't** modify `STAGES` list order in `stages.py` at runtime — the sidebar and progress bar indices depend on it

## COMMANDS
```bash
# Setup
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in ANTHROPIC_API_KEY

# Run
python main.py

# No tests, no linting, no build step — runs directly
```

## NOTES
- **Missing .gitignore** — `.venv/` and `__pycache__/` should be excluded
- **No tests** — zero test coverage
- **No `pyproject.toml`** — dependency management via `requirements.txt` only
- **Python 3.11+ required** — uses `X | Y` union syntax in type hints
- **Web search only works with Anthropic provider** — Ollama endpoints get no search capability
- **Stage loop is sequential** — stages run one after another, not in parallel

<!-- code-review-graph MCP tools -->
## MCP Tools: code-review-graph

**IMPORTANT: This project has a knowledge graph. ALWAYS use the
code-review-graph MCP tools BEFORE using Grep/Glob/Read to explore
the codebase.** The graph is faster, cheaper (fewer tokens), and gives
you structural context (callers, dependents, test coverage) that file
scanning cannot.

### When to use graph tools FIRST

- **Exploring code**: `semantic_search_nodes` or `query_graph` instead of Grep
- **Understanding impact**: `get_impact_radius` instead of manually tracing imports
- **Code review**: `detect_changes` + `get_review_context` instead of reading entire files
- **Finding relationships**: `query_graph` with callers_of/callees_of/imports_of/tests_for
- **Architecture questions**: `get_architecture_overview` + `list_communities`

Fall back to Grep/Glob/Read **only** when the graph doesn't cover what you need.

### Key Tools

| Tool | Use when |
|------|----------|
| `detect_changes` | Reviewing code changes — gives risk-scored analysis |
| `get_review_context` | Need source snippets for review — token-efficient |
| `get_impact_radius` | Understanding blast radius of a change |
| `get_affected_flows` | Finding which execution paths are impacted |
| `query_graph` | Tracing callers, callees, imports, tests, dependencies |
| `semantic_search_nodes` | Finding functions/classes by name or keyword |
| `get_architecture_overview` | Understanding high-level codebase structure |
| `refactor_tool` | Planning renames, finding dead code |

### Workflow

1. The graph auto-updates on file changes (via hooks).
2. Use `detect_changes` for code review.
3. Use `get_affected_flows` to understand impact.
4. Use `query_graph` pattern="tests_for" to check coverage.
