# Fix All 26 Verified Bugs

## TL;DR

> **Quick Summary**: Fix all 26 verified bugs across 4 source files (main.py, researcher.py, config.py, exporter.py) plus project root (.gitignore, test_event.py deletion), ordered by severity and grouped by file to minimize merge conflicts.
> 
> **Deliverables**:
> - Fixed main.py (20 bugs)
> - Fixed researcher.py (3 bugs)
> - Fixed config.py (1 bug)
> - Fixed exporter.py (1 bug)
> - New .gitignore
> - Deleted test_event.py
> 
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 5 waves
> **Critical Path**: Task 1 → Task 5 → Task 8 → Task 12 → Verification

---

## Context

### Original Request
Fix all 26 verified bugs identified in the Prode code review.

### Interview Summary
**Key Discussions**:
- User wants ALL 26 bugs fixed in one plan
- No test infrastructure — agent QA verification only
- Priority: Critical → Significant → Moderate → Low → Minor

**Research Findings**:
- Metis identified overlap risks (bugs sharing code regions must be fixed sequentially top-to-bottom)
- Metis flagged that `_advance_event` creation on wrong event loop is more subtle than just "move the init line"
- Dual-buffer architecture (`_output_buffer` + `_stage_buffer`) must be preserved
- QA must use static verification (`python -c "import ..."`) and TUI smoke test (`timeout 3 python main.py`)

### Metis Review
**Identified Gaps** (addressed):
- Overlap risk: bugs sharing same code region → tasks grouped by file, ordered top-to-bottom
- Scope creep risk (adding dependencies, refactoring, logging) → explicit guardrails set
- QA for TUI apps: Playwright won't work → static import checks + smoke test
- `asyncio.Event()` must be created on correct loop, not just "moved from __init__"
- `export_all_stages()` dead code → delete it (bug-fix pass, not feature pass)
- `test_event.py` → delete, don't fix

---

## Work Objectives

### Core Objective
Fix all 26 verified bugs in the Prode project, preserving existing architecture and conventions.

### Concrete Deliverables
- main.py: 20 bugs fixed
- researcher.py: 3 bugs fixed
- config.py: 2 bugs fixed
- exporter.py: 1 bug fixed
- New .gitignore file
- Deleted test_event.py

### Definition of Done
- [ ] `python -c "import main; import researcher; import config; import exporter"` exits 0
- [ ] `timeout 3 python main.py 2>&1 || true` shows no import/startup crash
- [ ] All 26 bugs addressed per acceptance criteria below
- [ ] No new linter errors introduced (check with `python -m py_compile main.py researcher.py config.py exporter.py`)

### Must Have
- All 26 bugs fixed with specific, targeted changes
- Each fix targets only the bug described — no refactoring beyond what's needed
- `.gitignore` containing `.venv/`, `__pycache__/`, `.env`, `*.pyc`

### Must NOT Have (Guardrails)
- NO new pip dependencies
- NO modifications to `prompt_template` strings in stages.py
- NO merging of `_output_buffer` and `_stage_buffer` — they serve different purposes
- NO test framework, test files, or test infrastructure added
- NO logging, validation forms, confirmation dialogs, or settings panels
- NO extraction of common error handlers (fix in-place only)
- NO changes to CSS layout unless the bug explicitly names a CSS file:line
- NO import of new third-party libraries (stdlib only for new code)

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: NO
- **Automated tests**: None
- **Framework**: N/A

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Static verification**: Bash — `python -c "import ..."` and `python -m py_compile ...`
- **Logic verification**: Bash — `python -c "from config import load_config; print(load_config())"` etc.
- **TUI smoke test**: Bash — `timeout 3 python main.py 2>&1 || true`
- **Code search**: Bash — `grep -n "PATTERN" FILE` to verify fix presence/absence

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately — non-overlapping, safe, separate files):
├── Task 1: Create .gitignore [quick]
├── Task 2: Delete test_event.py [quick]
└── Task 3: Fix exporter.py — Bug #23 slugify sanitization [quick]

Wave 2 (After Wave 1 — researcher.py, all 3 bugs in one file):
└── Task 4: Fix researcher.py — Bugs #3, #5, #7, #11 (top-to-bottom) [unspecified-high]

Wave 3 (After Wave 2 — config.py 2 bugs):
└── Task 5: Fix config.py — Bugs #9, #22 [quick]

Wave 4 (After Wave 3 — main.py, largest group, top-to-bottom):
├── Task 6: Fix main.py bugs #19, #8, #22 (init/modal region, lines 225-503) [unspecified-high]
├── Task 7: Fix main.py bugs #14, #15, #17 (event handler region, lines 370-570) [unspecified-high]
└── Task 8: Fix main.py bugs #1, #2, #3, #4, #6, #10, #13, #16, #18, #20, #21, #26 (worker/helper region, lines 570-819) [deep]

Wave 5 (After Wave 4 — delete dead code):
└── Task 9: Delete dead code — Bug #25 export_all_stages() [quick]

Wave FINAL (After ALL tasks — 4 parallel reviews, then user okay):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)
-> Present results -> Get explicit user okay

Critical Path: Task 1 → Task 4 → Task 5 → Task 8 → Task 9 → F1-F4 → user okay
Parallel Speedup: ~50% faster than sequential
Max Concurrent: 3 (Wave 1)
```

### Dependency Matrix

| Task | Depends On | Blocks |
|------|-----------|--------|
| 1 | - | 9 |
| 2 | - | F1-F4 |
| 3 | - | F1-F4 |
| 4 | - | 5, 8 |
| 5 | 4 | 6 |
| 6 | 5 | 8 |
| 7 | 5 | 8 |
| 8 | 6, 7 | 9 |
| 9 | 1, 8 | F1-F4 |
| F1-F4 | 9 | user okay |

### Agent Dispatch Summary

- **Wave 1**: **3** — T1 → `quick`, T2 → `quick`, T3 → `quick`
- **Wave 2**: **1** — T4 → `unspecified-high`
- **Wave 3**: **1** — T5 → `quick`
- **Wave 4**: **3** — T6 → `unspecified-high`, T7 → `unspecified-high`, T8 → `deep`
- **Wave 5**: **1** — T9 → `quick`
- **FINAL**: **4** — F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

- [x] 1. Create .gitignore (Bug #12)

  **What to do**:
  - Create `.gitignore` at project root with entries: `.venv/`, `__pycache__/`, `.env`, `*.pyc`
  - Nothing else — no `.editorconfig`, no `pyproject.toml`, no additional entries

  **Must NOT do**:
  - Do not add `.editorconfig`, `pyproject.toml`, or any other project config files
  - Do not add entries for IDE-specific files (`.idea/`, `.vscode/`) unless they already exist in repo

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 3)
  - **Blocks**: Task 9
  - **Blocked By**: None

  **References**:
  - Project root: `/Users/mohamedabdulrahman/Prode/` — where `.gitignore` should be created
  - Metis directive: "Add .gitignore with `.venv/`, `__pycache__/`, `.env`, `*.pyc` only. Nothing else."

  **Acceptance Criteria**:
  - [ ] `.gitignore` exists at project root
  - [ ] Contains `.venv/`, `__pycache__/`, `.env`, `*.pyc`

  **QA Scenarios**:
  ```
  Scenario: .gitignore exists with required entries
    Tool: Bash
    Preconditions: Project root is /Users/mohamedabdulrahman/Prode/
    Steps:
      1. Run: test -f .gitignore && echo "EXISTS" || echo "MISSING"
      2. Run: grep -q "__pycache__" .gitignore && echo "HAS_PYCACHE" || echo "MISSING_PYCACHE"
      3. Run: grep -q ".venv" .gitignore && echo "HAS_VENV" || echo "MISSING_VENV"
      4. Run: grep -q ".env" .gitignore && echo "HAS_ENV" || echo "MISSING_ENV"
    Expected Result: EXISTS, HAS_PYCACHE, HAS_VENV, HAS_ENV all printed
    Failure Indicators: Any "MISSING*" output
    Evidence: .sisyphus/evidence/task-1-gitignore-check.txt
  ```

  **Commit**: YES (groups with Tasks 2, 3)
  - Message: `fix(root): add .gitignore, delete test_event.py, fix slugify`
  - Files: `.gitignore`
  - Pre-commit: `test -f .gitignore`

- [x] 2. Delete test_event.py (Bug #24)

  **What to do**:
  - Delete the file `test_event.py` from the project root
  - This is a scratchpad file with `print()` statements, `asyncio.run()`, and no assertions
  - It is not imported anywhere in the project

  **Must NOT do**:
  - Do not convert it to a real test file
  - Do not add test infrastructure
  - Do not create a replacement file

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3)
  - **Blocks**: F1-F4
  - **Blocked By**: None

  **References**:
  - `test_event.py` — the file to delete (24 lines, scratchpad)
  - AGENTS.md: "test_event.py is scratchpad, not real tests" (BUG 24)

  **Acceptance Criteria**:
  - [ ] `test_event.py` does not exist

  **QA Scenarios**:
  ```
  Scenario: test_event.py is deleted
    Tool: Bash
    Preconditions: test_event.py existed before fix
    Steps:
      1. Run: test -f test_event.py && echo "STILL_EXISTS" || echo "DELETED"
    Expected Result: "DELETED"
    Failure Indicators: "STILL_EXISTS"
    Evidence: .sisyphus/evidence/task-2-delete-test-event.txt
  ```

  **Commit**: YES (groups with Tasks 1, 3)
  - Message: `fix(root): add .gitignore, delete test_event.py, fix slugify`
  - Files: `test_event.py` (deleted)
  - Pre-commit: `test ! -f test_event.py`

- [x] 3. Fix slugify sanitization (Bug #23)

  **What to do**:
  - In `exporter.py`, function `slugify()` at line 11-15
  - Add path traversal protection: strip `..` and `/` from slug output
  - Current regex `r"[^\w\s-]"` already removes most special chars, but doesn't protect against `..` sequences that could survive if the input is crafted (e.g., `../../etc/passwd` → after first sub becomes `..etc-passwd` → after second sub becomes `..etc-passwd` → strip removes leading `-` but not `.`)
  - Add: after the existing regex substitutions, add `text = text.replace("..", "")` or strip leading dots
  - Keep the function simple — one additional line

  **Must NOT do**:
  - Do not add a validation library
  - Do not rewrite the function from scratch
  - Do not add filesystem path validation beyond dot-stripping

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2)
  - **Blocks**: F1-F4
  - **Blocked By**: None

  **References**:
  - `exporter.py:11-15` — the `slugify()` function to fix
  - Current code: `text = re.sub(r"[^\w\s-]", "", text)` then `text = re.sub(r"[-\s]+", "-", text)` then `return text[:50].strip("-")`

  **Acceptance Criteria**:
  - [ ] `slugify("../../etc/passwd")` returns a safe string without `..` or `/`
  - [ ] `slugify("AI-powered tool")` still returns `"ai-powered-tool"` (existing behavior preserved)

  **QA Scenarios**:
  ```
  Scenario: Path traversal is stripped
    Tool: Bash
    Preconditions: exporter.py has been modified
    Steps:
      1. Run: python3 -c "from exporter import slugify; print(repr(slugify('../../etc/passwd')))"
    Expected Result: Output does not contain ".." or "/"
    Failure Indicators: Output contains ".." or "/"
    Evidence: .sisyphus/evidence/task-3-slugify-safe.txt

  Scenario: Normal input still works
    Tool: Bash
    Steps:
      1. Run: python3 -c "from exporter import slugify; print(slugify('AI-powered tool'))"
    Expected Result: "ai-powered-tool"
    Failure Indicators: Any different output
    Evidence: .sisyphus/evidence/task-3-slugify-normal.txt
  ```

  **Commit**: YES (groups with Tasks 1, 2)
  - Message: `fix(root): add .gitignore, delete test_event.py, fix slugify`
  - Files: `exporter.py`
  - Pre-commit: `python3 -c "from exporter import slugify; slugify('../../test')"`

- [x] 4. Fix researcher.py — Bugs #3, #5, #7, #11 (top-to-bottom)

  **What to do**:
  Fix 4 bugs in researcher.py, ordered top-to-bottom by line number:

  **Bug #7 (line 149)**: Replace `asyncio.get_event_loop()` with `asyncio.get_running_loop()`
  - Line 149: `loop = asyncio.get_event_loop()` → `loop = asyncio.get_running_loop()`
  - This runs inside an async function, so `get_running_loop()` is correct and available

  **Bug #5 (lines 151-156)**: Make `_fetch_search_context` report search failures instead of silently returning empty
  - Currently: `except Exception: return []` at line 155
  - Fix: Log the failure and return empty list, but also consider adding a `logging.warning()` or yielding a user-visible signal
  - Simplest fix: Add a comment and change the bare except to catch specific exceptions (`requests.RequestException`, `Exception`) — but since the function is called from `_stream_ollama`, the best approach is to return the empty list but propagate a hint that search failed
  - Recommended: Add `import logging; logger = logging.getLogger(__name__)` at module level, then `except Exception as exc: logger.warning("Search failed: %s", exc); return []`
  - No new dependencies — `logging` is stdlib

  **Bug #11 (lines 192-194)**: Only emit search events if search actually returned results
  - Lines 192-194: `yield ("searching", "")` and `yield ("search_done", "")` are emitted unconditionally
  - Fix: Move the `yield ("searching", "")` before the search call (keep it), but only yield `("search_done", "")` if `search_context` is not empty
  - Change `yield ("search_done", "")` at line 194 to: `if search_context: yield ("search_done", "")`
  - This prevents the UI from flickering "Searching the web…" → "done" when no results were found

  **Bug #3 (line 185)**: Add `APITimeoutError` to the openai import and catch it
  - Line 185: `from openai import AsyncOpenAI, APIConnectionError, RateLimitError, APIStatusError`
  - Add `APITimeoutError` to the import
  - Add a catch block after `RateLimitError`: `except APITimeoutError: yield ("rate_limit", "")`
  - This treats timeouts the same as rate limits (retryable), matching the Anthropic path behavior

  **Must NOT do**:
  - Do not add all Anthropic/openai exception types "for completeness" — only `APITimeoutError`
  - Do not refactor the streaming functions into a shared base
  - Do not add a requests dependency for search error handling — use stdlib `logging`
  - Do not modify the Anthropic streaming path (`_stream_anthropic`)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []
    - Multiple bug fixes in single file, requires careful ordering and understanding of streaming event protocol

  **Parallelization**:
  - **Can Run In Parallel**: NO (single file, multiple dependent changes)
  - **Parallel Group**: Wave 2 (sequential within task)
  - **Blocks**: Task 5, Task 8
  - **Blocked By**: None

  **References**:
  - `researcher.py:149` — `asyncio.get_event_loop()` to replace
  - `researcher.py:151-156` — `_sync_search()` exception swallowing to fix
  - `researcher.py:192-194` — search event yields to condition
  - `researcher.py:185` — openai import to extend
  - `researcher.py:216-223` — exception handlers to add `APITimeoutError` before the generic `Exception`
  - `main.py:705-718` — how `rate_limit` events are handled (retry loop) — confirms `APITimeoutError` should yield `("rate_limit", "")` for retry

  **Acceptance Criteria**:
  - [ ] `asyncio.get_event_loop()` no longer appears in researcher.py
  - [ ] `APITimeoutError` appears in the openai import at line 185
  - [ ] `APITimeoutError` catch block exists before `APIConnectionError` in `_stream_ollama`
  - [ ] Search events conditional on `search_context` being non-empty
  - [ ] Search failures logged via `logging.warning()` instead of silently swallowed

  **QA Scenarios**:
  ```
  Scenario: No deprecated asyncio calls in researcher.py
    Tool: Bash
    Steps:
      1. Run: grep -n "get_event_loop" researcher.py
    Expected Result: No output (no matches)
    Failure Indicators: Any line matches
    Evidence: .sisyphus/evidence/task-4-no-deprecated-asyncio.txt

  Scenario: APITimeoutError is imported and caught
    Tool: Bash
    Steps:
      1. Run: grep -n "APITimeoutError" researcher.py
    Expected Result: At least 2 matches (import line + catch block)
    Failure Indicators: Fewer than 2 matches
    Evidence: .sisyphus/evidence/task-4-timeout-import.txt

  Scenario: Import check passes
    Tool: Bash
    Steps:
      1. Run: python3 -c "import researcher; print('OK')"
    Expected Result: "OK"
    Failure Indicators: ImportError, ModuleNotFoundError, or any exception
    Evidence: .sisyphus/evidence/task-4-import-check.txt

  Scenario: Search done event is conditional
    Tool: Bash
    Steps:
      1. Run: grep -A1 "search_done" researcher.py | head -5
    Expected Result: Shows conditional yield (if search_context check)
    Failure Indicators: Unconditional yield of search_done
    Evidence: .sisyphus/evidence/task-4-search-conditional.txt
  ```

  **Commit**: YES
  - Message: `fix(researcher): add APITimeoutError, fix search error handling, use get_running_loop`
  - Files: `researcher.py`
  - Pre-commit: `python3 -c "import researcher"`

- [x] 5. Fix config.py — Bugs #9, #22

  **What to do**:

  **Bug #22 (lines 229-232 in main.py, but root cause in config.py:32-34)**: Validate config before saving
  - Currently `save_config()` at config.py:32-34 writes whatever it receives
  - Fix: Add a basic validation check in `save_config()` before writing
  - Validate that `config.provider` is one of the known providers ("anthropic", "ollama_local", "ollama_cloud")
  - If validation fails, raise `ValueError` — the caller in `main.py:229-231` already handles this (the `_submit` method checks `_build_config()` return value)
  - Actually, looking again: `_build_config()` already validates (returns None for invalid). The real issue is `save_config(config)` is called at line 230 BEFORE `_build_config()` could have returned None. But line 229 checks `if config:` first. So Bug #22 is about **minimal validation** — the fix is to ensure `save_config` doesn't write garbage.
  - Simplest fix: Add a type check in `save_config` — `if not isinstance(config, ProviderConfig): raise TypeError(...)` — purely defensive

  **Bug #9 (config.py:28-29)**: Warn when corrupted config is discarded
  - Currently: `except (json.JSONDecodeError, KeyError, TypeError): return None`
  - Fix: Add `logging.warning()` before returning None, so users know their config was corrupted
  - Add `import logging; logger = logging.getLogger(__name__)` at top of config.py
  - Change except block to: `except (json.JSONDecodeError, KeyError, TypeError) as exc: logger.warning("Config file corrupted, resetting: %s", exc); return None`

  **Must NOT do**:
  - Do not add undo/confirmation to config changes
  - Do not add a config migration system
  - Do not add pydantic or any validation library

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on Task 4 completing — researcher.py changes affect ProviderConfig)
  - **Parallel Group**: Wave 3
  - **Blocks**: Tasks 6, 7, 8
  - **Blocked By**: Task 4

  **References**:
  - `config.py:16-29` — `load_config()` function
  - `config.py:32-34` — `save_config()` function
  - `main.py:226-231` — caller of `save_config()`, already checks for None

  **Acceptance Criteria**:
  - [ ] `load_config()` logs a warning when config is corrupted instead of silently returning None
  - [ ] `save_config()` validates input type before writing
  - [ ] `python3 -c "from config import load_config, save_config; print('OK')"` passes

  **QA Scenarios**:
  ```
  Scenario: Corrupted config logs warning
    Tool: Bash
    Steps:
      1. Run: python3 -c "
import json, tempfile, os
from pathlib import Path
import config
config.CONFIG_PATH = Path(tempfile.mktemp())
config.CONFIG_PATH.write_text('{corrupted json')
result = config.load_config()
print(f'Result: {result}')
"
    Expected Result: "Result: None" (still returns None, but warning logged)
    Failure Indicators: Exception raised (should not crash)
    Evidence: .sisyphus/evidence/task-5-corrupted-config.txt

  Scenario: Import check passes
    Tool: Bash
    Steps:
      1. Run: python3 -c "import config; print('OK')"
    Expected Result: "OK"
    Failure Indicators: ImportError
    Evidence: .sisyphus/evidence/task-5-import-check.txt
  ```

  **Commit**: YES
  - Message: `fix(config): warn on corrupted config, validate before save`
  - Files: `config.py`
  - Pre-commit: `python3 -c "import config"`

- [x] 6. Fix main.py bugs in init/modal region — Bugs #19, #8, #22 (lines 225-503)

  **What to do**:
  Fix 3 bugs in main.py's init and modal region, top-to-bottom:

  **Bug #8 (lines 237-239)**: Give user feedback when Anthropic key is empty
  - Currently: `if not key: return None` — user gets no feedback, modal just closes
  - Fix: Show a notification before returning None
  - Add `self.app.notify("Please enter an API key.", severity="warning")` and then return None
  - Note: this is inside `ProviderSetupModal._build_config()`, which doesn't have a `notify` method directly, but `self.app` does since it's a modal screen

  **Bug #22 (lines 229-232)**: Validate config before save
  - Actually: Looking at this more carefully, the code at lines 229-232 already guards with `if config:`. The real issue is that `_build_config()` only checks for empty strings — it doesn't validate the API key format or URL format. This is LOW severity.
  - Fix: Add a minimum-length check for the API key (e.g., `len(key) < 10` suggests it's probably wrong)
  - In `_build_config()` at the Anthropic branch (line 237-240): after checking `if not key:`, add `elif len(key) < 10: self.app.notify("API key seems too short — please check it.", severity="warning"); return None`
  - This is a soft validation — it doesn't prevent saves, just warns

  **Bug #19 (line 503)**: Initialize `_advance_event` on the correct event loop
  - Currently: `self._advance_event: asyncio.Event = asyncio.Event()` in `__init__` (line 503)
  - The issue: `asyncio.Event()` created in `__init__` runs before the Textual event loop exists. In Python 3.12+ this emits DeprecationWarning. The Event is recreated at line 673 in `_run_all_stages()` which IS on the correct loop.
  - Fix: Change line 503 to `self._advance_event: asyncio.Event | None = None`
  - Then in `_run_all_stages()` line 673 (which already does `self._advance_event = asyncio.Event()`), the Event is created on the correct loop
  - Also need to handle the `None` case: any method that uses `self._advance_event` before `_run_all_stages()` must check for None
  - Lines using `_advance_event`: 677 (set), 742 (clear), 749 (wait), 677 (creation in worker)
  - All of these are inside `_run_all_stages()` AFTER line 673 creates it, so None check is not needed there
  - But `_on_next_pressed` at line 564 calls `self._advance_event.set()` — this could be called before the worker starts. Add a guard: `if self._advance_event is not None: self._advance_event.set()`

  **Must NOT do**:
  - Do not add form validation to the modal beyond the API key length check
  - Do not move all init logic to `on_mount()` — only fix the Event initialization
  - Do not add `from __future__ import annotations`

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []
  - Multiple fixes in same region, requires understanding Textual lifecycle

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4 (with Tasks 7, 8)
  - **Blocks**: Task 8
  - **Blocked By**: Task 5

  **References**:
  - `main.py:237-239` — empty key check in `_build_config()`
  - `main.py:229-232` — `_submit()` that calls `save_config()`
  - `main.py:503` — `asyncio.Event()` initialization in `__init__`
  - `main.py:564` — `_on_next_pressed()` that calls `_advance_event.set()`
  - `main.py:673` — `_advance_event` recreation in `_run_all_stages()` (this is already correct — creates on right loop)
  - `main.py:677,742,749` — other uses of `_advance_event` (all inside worker, after line 673)

  **Acceptance Criteria**:
  - [ ] User gets a notification when submitting with empty Anthropic key
  - [ ] `asyncio.Event()` no longer created in `__init__`; `_advance_event` starts as `None`
  - [ ] `_on_next_pressed()` guards against `_advance_event is None`
  - [ ] `_advance_event` is created on the correct event loop in `_run_all_stages()`

  **QA Scenarios**:
  ```
  Scenario: No asyncio.Event in __init__
    Tool: Bash
    Steps:
      1. Run: grep -n "asyncio.Event()" main.py | head -5
    Expected Result: Only appears inside _run_all_stages (around line 673), not in __init__
    Failure Indicators: asyncio.Event() appears in __init__ region (around line 503)
    Evidence: .sisyphus/evidence/task-6-no-event-init.txt

  Scenario: _advance_event starts as None
    Tool: Bash
    Steps:
      1. Run: grep -n "_advance_event" main.py | head -10
    Expected Result: First occurrence shows initialization as None
    Failure Indicators: First occurrence still creates asyncio.Event()
    Evidence: .sisyphus/evidence/task-6-event-none.txt

  Scenario: Import check passes
    Tool: Bash
    Steps:
      1. Run: python3 -c "import main; print('OK')"
    Expected Result: "OK"
    Failure Indicators: ImportError or DeprecationWarning
    Evidence: .sisyphus/evidence/task-6-import-check.txt
  ```

  **Commit**: YES (groups with Tasks 7, 8)
  - Message: `fix(main): fix all 17 bugs — unbound var, rate limit, streaming, events, shortcuts`
  - Files: `main.py`
  - Pre-commit: `python3 -c "import main"`

- [x] 7. Fix main.py bugs in event handler region — Bugs #14 (partial), #15, #17 (lines 370-570)

  **What to do**:
  Fix 3 bugs in main.py's event handler / widget region:

  **Bug #14 (partial — 2 of 6 bare excepts in this region)**:
  - Line 383: `except Exception: pass` in `StatusBar.set_status()` — change to `except Exception: pass` (keep as-is, this is defensive UI code where widget may not exist yet — but add a comment `# noqa: BLE001 — widget may not exist yet`)
  - Line 388: same pattern — add comment only
  - For these two, the bare except IS intentional (widget queries fail if screen not mounted yet). Just add the `# noqa` comments.
  - The remaining 4 bare excepts in the worker/helper region are handled in Task 8.

  **Bug #15 (lines 517-518)**: Add keyboard shortcut for "Next" button
  - Currently: User must click "Next" button to advance between stages
  - Fix: Add a keybinding for advancing. Add `Binding("n", "advance_stage", "Next stage")` or use the existing binding system
  - Look at main.py `BINDINGS` list (around line 416) for the pattern
  - Add an `action_advance_stage` method that calls `self._advance_event.set()` (same as clicking Next)
  - Alternatively, bind "n" key to the same logic as `_on_next_pressed`

  **Bug #17 (lines 564-567)**: Guard against double-clicking Next/Run buttons
  - Currently: No guard against rapid clicks
  - Fix: Disable the button immediately on press, re-enable after action completes
  - In `_on_next_pressed` (line 564): add `self.query_one("#next-btn", Button).disabled = True` before setting the event
  - In `_run_all_stages` before showing the Next button (line 747): ensure `btn.disabled = False`
  - Also guard `_submit` (Run button): add a disabled check or disable button immediately

  **Must NOT do**:
  - Do not add logging to the bare except blocks — just add noqa comments
  - Do not add a "settings panel" for keyboard shortcuts
  - Do not add debouncing — just disable/re-enable the button

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4 (with Tasks 6, 8)
  - **Blocks**: Task 8
  - **Blocked By**: Task 5

  **References**:
  - `main.py:383,388` — bare excepts in StatusBar (add noqa comments)
  - `main.py:416` — BINDINGS list pattern for keybindings
  - `main.py:517-518` — Next button definition
  - `main.py:564-567` — `_on_next_pressed` handler
  - `main.py:747` — where Next button is shown again after stage completes

  **Acceptance Criteria**:
  - [ ] Bare excepts at lines 383, 388 have `# noqa: BLE001` comments
  - [ ] "n" key triggers advance between stages
  - [ ] Next button is disabled immediately on click, re-enabled when shown again

  **QA Scenarios**:
  ```
  Scenario: Keybinding for Next stage exists
    Tool: Bash
    Steps:
      1. Run: grep -n "advance_stage\|next.*key\|Binding.*n" main.py | head -5
    Expected Result: At least one match showing n/N keybinding for advancing
    Failure Indicators: No matches
    Evidence: .sisyphus/evidence/task-7-keybinding.txt

  Scenario: Button disabled on click
    Tool: Bash
    Steps:
      1. Run: grep -n "disabled" main.py | head -10
    Expected Result: Shows disabled = True in _on_next_pressed, disabled = False when showing button
    Failure Indicators: No disabled guard found
    Evidence: .sisyphus/evidence/task-7-button-guard.txt

  Scenario: Import check passes
    Tool: Bash
    Steps:
      1. Run: python3 -c "import main; print('OK')"
    Expected Result: "OK"
    Evidence: .sisyphus/evidence/task-7-import-check.txt
  ```

  **Commit**: YES (groups with Tasks 6, 8)
  - Message: `fix(main): fix all 17 bugs — unbound var, rate limit, streaming, events, shortcuts`
  - Files: `main.py`

- [x] 8. Fix main.py bugs in worker/helper region — Bugs #1, #2, #4, #6, #10, #13, #14 (remaining 4), #16, #18, #20, #21, #26 (lines 570-819)

  **What to do**:
  Fix 12 bugs in main.py's worker loop and helper region, top-to-bottom:

  **Bug #1 (line 764)**: Guard `status_bar` in exception handler
  - Currently: `status_bar.set_status(...)` in except block at line 764, but `status_bar` is assigned inside the try block at ~line 672
  - If exception occurs before line 672, `status_bar` is unbound → `UnboundLocalError`
  - Fix: Either (a) move `status_bar = self.query_one(StatusBar)` before the try block, or (b) add a guard `if 'status_bar' in dir(): status_bar.set_status(...)` or (c) wrap in try/except
  - Best fix: Use `self._set_status(...)` helper (line 808-812) which already has try/except, instead of `status_bar.set_status(...)` directly

  **Bug #2 (lines 693-734)**: Reset `stage_text` on rate-limit retry
  - Currently: `stage_text += content` accumulates text, then on rate-limit, the `break` exits the inner loop and the outer `while should_retry` re-runs the entire stream — but `stage_text` still has the partial text from the failed attempt
  - Fix: Reset `self._stage_buffer = ""` and `self._output_buffer` tracking before each retry attempt
  - Add `stage_text = ""` after the `while should_retry:` line, before re-entering the stream
  - Also need to clear the display: reset `_stage_buffer` and call `_flush_output`

  **Bug #6 (line 738)**: Only increment progress bar on success
  - Currently: `status_bar.set_progress(idx + 1)` at line 738 runs regardless of `success`
  - Fix: Change to `status_bar.set_progress(idx + 1 if success else idx)` or only increment on success and add a separate "failed" progress indicator

  **Bug #10 (line 737)**: Stop sidebar spinner on unrecoverable error
  - Currently: `sidebar.set_status(stage.id, "done" if success else "failed")` at line 737 — this sets the sidebar status but the spinner logic might not check for "failed"
  - Fix: Verify the `StagesSidebar.set_status()` handles "failed" state to stop the spinner. If it doesn't, add explicit stop.
  - Looking at the sidebar widget code — need to check if "failed" stops the spinner animation

  **Bug #4 (line 794)**: Render markdown during flush instead of plain text
  - Currently: `_flush_output()` at line 791-797 updates widget with plain `self._stage_buffer`
  - Fix: Use `RichMarkdown(self._stage_buffer)` instead of plain text during flush
  - But RichMarkdown parsing is expensive — the original design uses plain text during streaming for performance, then renders markdown at stage end via `_render_markdown()`
  - Compromise: Use `Markdown` (lighter than `RichMarkdown`) during flush, or add a small debounce/throttle so we don't parse markdown on every single token
  - Simplest fix that improves UX: In `_flush_output()`, try to render as `RichMarkdown` with a try/except fallback to plain text. This leverages the existing `_render_markdown()` pattern.
  - Actually, the simplest meaningful improvement: Change `_flush_output` to call `self._render_markdown()` instead of plain text update. The `_render_markdown()` already runs in an executor for non-blocking parsing.

  **Bug #13 (line 795)**: Stop auto-scrolling when user manually scrolls up
  - Currently: `scroll_end(animate=False)` fires on every flush, overriding user scroll
  - Fix: Only auto-scroll if the user is already at/near the bottom
  - Add a check: `if scroll_widget.is_at_bottom(): scroll_widget.scroll_end(animate=False)` (or similar Textual API)
  - Textual's `VerticalScroll` has a `is_scroll_at_bottom()` or similar — check the API
  - Alternative: Track a `_user_scrolled` flag that's set on scroll events and cleared on new stage

  **Bug #14 (remaining 4 bare excepts at lines 614, 797, 806, 812)**:
  - Line 614: `except Exception: pass` in initial output update during research start — add specific exception type `except Exception: pass  # noqa: BLE001 — widget may not be mounted yet`
  - Line 797: `except Exception: pass` in `_flush_output` — same, add comment
  - Line 806: `except Exception: pass` in `_render_markdown` — this should fall back to plain text. Already handled. Add comment: `# noqa: BLE001 — fallback to plain text on parse failure`
  - Line 812: `except Exception: pass` in `_set_status` — same, add comment
  - For lines 797, 806: These are the "fallback" pattern — intentionally broad. Just add noqa comments.

  **Bug #16 (lines 714-718)**: Add exponential backoff for rate limits
  - Currently: Fixed 5-second wait between retries
  - Fix: Implement simple exponential backoff: `wait_time = RATE_LIMIT_WAIT * (2 ** (retries - 1))`
  - Change the `for secs in range(RATE_LIMIT_WAIT, 0, -1):` loop to use the backoff time
  - Keep the countdown display but use the calculated wait time
  - Example: 1st retry: 5s, 2nd retry: 10s, 3rd retry: 20s

  **Bug #18 (line 749)**: Add timeout to `_advance_event.wait()`
  - Currently: `await self._advance_event.wait()` blocks indefinitely
  - Fix: Use `await asyncio.wait_for(self._advance_event.wait(), timeout=300)` (5 minutes)
  - If timeout expires, treat it like the user closed the app — show an error and stop
  - Add `except asyncio.TimeoutError:` handler that shows a notification and stops the research

  **Bug #20 (lines 741-748)**: Show failure notification in yolo mode when stage fails
  - Currently: In yolo mode, failed stages are auto-advanced past without notification
  - Fix: Check `if self._yolo_mode and not success:` and show a notification like "Stage {name} failed — auto-advancing…"
  - Add before the yolo mode advance logic

  **Bug #21 (lines 799-806)**: Clear partial markdown on render failure
  - Currently: If `_render_markdown()` fails, the plain text fallback keeps partial/broken markdown in the display
  - Fix: On exception in `_render_markdown()`, explicitly update with `Static.update(self._stage_buffer)` (plain text) — this is what the current `pass` is supposed to do, but it doesn't actually update the widget
  - Change the `except Exception: pass` to `except Exception: self.query_one("#output-md", Static).update(self._stage_buffer)` — keeps plain text visible

  **Bug #26 (line 616)**: Add ellipsis to truncated notification
  - Currently: `self.notify(f"Starting research for: {idea[:50]}")` truncates without indication
  - Fix: Change to `self.notify(f"Starting research for: {idea[:47]}...")` if `len(idea) > 50`, otherwise use full idea
  - Simple: `display_idea = idea if len(idea) <= 50 else idea[:47] + "..."`

  **Must NOT do**:
  - Do not merge `_output_buffer` and `_stage_buffer`
  - Do not add Playwright/tests for the TUI
  - Do not add a scroll event listener for Bug #13 if the Textual API already provides `is_at_bottom()`
  - Do not add configurable timeout for Bug #18 — fixed 300s is fine

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []
  - This is the largest task — 12 bugs in the worker loop, requires careful sequential application and understanding of the stage pipeline

  **Parallelization**:
  - **Can Run In Parallel**: NO (same file as Tasks 6, 7, changes must be applied after those)
  - **Parallel Group**: Wave 4 (after Tasks 6, 7)
  - **Blocks**: Task 9
  - **Blocked By**: Tasks 6, 7

  **References**:
  - `main.py:672` — `status_bar = self.query_one(StatusBar)` (assigned in try block)
  - `main.py:762-765` — `except Exception` block that references `status_bar` (Bug #1)
  - `main.py:808-812` — `_set_status()` helper with safe try/except (alternative for Bug #1)
  - `main.py:693-734` — rate limit retry loop with `stage_text` accumulation (Bug #2)
  - `main.py:738` — progress bar increment regardless of success (Bug #6)
  - `main.py:737` — sidebar status update (Bug #10)
  - `main.py:791-797` — `_flush_output()` with plain text (Bug #4)
  - `main.py:799-806` — `_render_markdown()` with parse fallback (Bugs #4, #21)
  - `main.py:795` — `scroll_end` fighting user scroll (Bug #13)
  - `main.py:614,797,806,812` — bare except locations (Bug #14 partial)
  - `main.py:714-718` — fixed rate limit wait (Bug #16)
  - `main.py:749` — `_advance_event.wait()` with no timeout (Bug #18)
  - `main.py:741-748` — yolo mode advance logic (Bug #20)
  - `main.py:616` — notification truncation (Bug #26)
  - `researcher.py:149` — already fixed in Task 4 (context for understanding event loop)

  **Acceptance Criteria**:
  - [ ] No `UnboundLocalError` possible for `status_bar` in exception handler
  - [ ] `stage_text` reset on rate-limit retry
  - [ ] Progress bar only increments on successful stages
  - [ ] Sidebar spinner stops on failure
  - [ ] Markdown rendered during streaming (or at least better than plain text)
  - [ ] Auto-scroll respects user scroll position
  - [ ] All bare excepts have `# noqa` comments
  - [ ] Exponential backoff for rate-limit retries
  - [ ] 5-minute timeout on stage advance wait
  - [ ] Yolo mode shows failure notification
  - [ ] Markdown render failure falls back to plain text explicitly
  - [ ] Truncated notification shows ellipsis

  **QA Scenarios**:
  ```
  Scenario: status_bar no longer unbound in except block
    Tool: Bash
    Steps:
      1. Run: grep -A3 "except Exception as exc:" main.py | grep "status_bar\|_set_status" | head -3
    Expected Result: Except block uses _set_status() or guards status_bar access
    Failure Indicators: Except block still directly references potentially-unbound status_bar
    Evidence: .sisyphus/evidence/task-8-status-bar-guard.txt

  Scenario: stage_text is reset on retry
    Tool: Bash
    Steps:
      1. Run: grep -B2 -A2 "should_retry" main.py | head -20
    Expected Result: stage_text = "" appears before each retry attempt
    Failure Indicators: stage_text not reset between retries
    Evidence: .sisyphus/evidence/task-8-retry-reset.txt

  Scenario: Exponential backoff exists
    Tool: Bash
    Steps:
      1. Run: grep -n "backoff\|2 \*\*\|exponential\|RATE_LIMIT_WAIT" main.py | head -10
    Expected Result: Shows backoff calculation (2**retries or similar)
    Failure Indicators: Still uses fixed wait time
    Evidence: .sisyphus/evidence/task-8-backoff.txt

  Scenario: Timeout on advance_event.wait
    Tool: Bash
    Steps:
      1. Run: grep -n "wait_for\|TimeoutError\|_advance_event.wait" main.py | head -5
    Expected Result: Shows wait_for with timeout or TimeoutError handler
    Failure Indicators: Still uses bare await .wait()
    Evidence: .sisyphus/evidence/task-8-timeout.txt

  Scenario: Full import and compile check
    Tool: Bash
    Steps:
      1. Run: python3 -m py_compile main.py && echo "COMPILE_OK" || echo "COMPILE_FAIL"
      2. Run: python3 -c "import main; print('IMPORT_OK')"
    Expected Result: COMPILE_OK and IMPORT_OK
    Failure Indicators: Compile or import error
    Evidence: .sisyphus/evidence/task-8-compile-check.txt

  Scenario: TUI smoke test — app starts without crash
    Tool: Bash
    Steps:
      1. Run: timeout 3 python3 main.py 2>&1 || true
    Expected Result: No import errors, no immediate crash, app starts (even though it exits due to timeout)
    Failure Indicators: ImportError, ModuleNotFoundError, DeprecationWarning on asyncio.Event
    Evidence: .sisyphus/evidence/task-8-smoke-test.txt
  ```

  **Commit**: YES (groups with Tasks 6, 7)
  - Message: `fix(main): fix all 17 bugs — unbound var, rate limit, streaming, events, shortcuts`
  - Files: `main.py`
  - Pre-commit: `python3 -m py_compile main.py && python3 -c "import main"`

- [x] 9. Delete dead code — Bug #25 export_all_stages()

  **What to do**:
  - Delete the `export_all_stages()` function from `exporter.py` (lines 53-88)
  - This function is never called anywhere in the codebase
  - Verify no references: `grep -r "export_all_stages" *.py` should return 0 results after deletion

  **Must NOT do**:
  - Do not wire it up to a new feature
  - Do not refactor the remaining `export_results()` function

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (needs Tasks 1 and 8 to complete first)
  - **Parallel Group**: Wave 5
  - **Blocks**: F1-F4
  - **Blocked By**: Tasks 1, 8

  **References**:
  - `exporter.py:53-88` — `export_all_stages()` function to delete
  - `main.py:34` — only imports `export_results`, not `export_all_stages`

  **Acceptance Criteria**:
  - [ ] `export_all_stages` no longer exists in exporter.py
  - [ ] `grep -r "export_all_stages" *.py` returns 0 matches

  **QA Scenarios**:
  ```
  Scenario: Dead code removed
    Tool: Bash
    Steps:
      1. Run: grep -c "export_all_stages" exporter.py
    Expected Result: 0
    Failure Indicators: Any matches (>0)
    Evidence: .sisyphus/evidence/task-9-dead-code-removed.txt

  Scenario: Import check still passes
    Tool: Bash
    Steps:
      1. Run: python3 -c "from exporter import export_results; print('OK')"
    Expected Result: "OK"
    Failure Indicators: ImportError
    Evidence: .sisyphus/evidence/task-9-import-check.txt
  ```

  **Commit**: YES
  - Message: `fix(exporter): remove dead export_all_stages function`
  - Files: `exporter.py`
  - Pre-commit: `python3 -c "from exporter import export_results"`

---

## Final Verification Wave

- [x] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, check command). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [x] F2. **Code Quality Review** — `unspecified-high`
  Run `python -m py_compile main.py researcher.py config.py exporter.py`. Review all changed files for: `as any` type casts, empty catches that weren't there before, new console.log/print, commented-out code, unused imports. Check AI slop: excessive comments, over-abstraction, generic names.
  Output: `Compile [PASS/FAIL] | Files [N clean/N issues] | VERDICT`

- [x] F3. **Manual QA** — `unspecified-high`
  Start from clean state. Run `python -c "import main; import researcher; import config; import exporter"` — must succeed. Run `timeout 3 python main.py 2>&1 || true` — must not crash on startup. Verify `.gitignore` exists with required entries. Verify `test_event.py` does not exist.
  Output: `Import [PASS/FAIL] | Smoke [PASS/FAIL] | Gitignore [PASS/FAIL] | VERDICT`

- [x] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff. Verify 1:1 — everything in spec was built (no missing), nothing beyond spec was built (no creep). Check "Must NOT do" compliance. Detect cross-task contamination.
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

- **Task 1+2+3**: `fix(root): add .gitignore, delete test_event.py, fix slugify`
- **Task 4**: `fix(researcher): add APITimeoutError, fix search error handling, use get_running_loop`
- **Task 5**: `fix(config): warn on corrupted config, validate before save`
- **Task 6+7+8**: `fix(main): fix all 17 bugs — unbound var, rate limit, streaming, events, shortcuts`
- **Task 9**: `fix(exporter): remove dead export_all_stages function`
- Pre-commit for each: `python -m py_compile main.py researcher.py config.py exporter.py`

---

## Success Criteria

### Verification Commands
```bash
python -c "import main; import researcher; import config; import exporter"  # Expected: no output (exit 0)
python -m py_compile main.py researcher.py config.py exporter.py            # Expected: no output (exit 0)
timeout 3 python main.py 2>&1 || true                                      # Expected: no import/startup crash
test -f .gitignore && grep -q __pycache__ .gitignore                        # Expected: exit 0
test ! -f test_event.py                                                      # Expected: exit 0 (file deleted)
grep -c "export_all_stages" exporter.py                                      # Expected: 0 (dead code removed)
```

### Final Checklist
- [ ] All 26 bugs addressed
- [ ] No new pip dependencies
- [ ] No stages.py modifications
- [ ] Dual-buffer architecture preserved
- [ ] Import check passes
- [ ] Smoke test passes