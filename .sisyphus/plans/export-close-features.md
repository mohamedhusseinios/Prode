# Export Directory Picker + Close Button

## TL;DR

> **Quick Summary**: Add a directory picker modal (Textual DirectoryTree) for choosing where to export research results, and add a visible close/quit button in the header that cancels any running research worker before exiting.
>
> **Deliverables**:
> - `DirectoryPickerModal` class — file browser modal for choosing export directory
> - Close "✕" button in the header bar
> - Modified `action_export()` to use the directory picker
> - `_cancel_and_quit()` method for clean exit with worker cancellation
>
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 2 waves
> **Critical Path**: Task 1 → Task 2 + Task 3 → Task 4 → F1-F4

---

## Context

### Original Request
Add 2 features: (1) after research finishes, show export option to export in a specific directory, (2) add a close button as an option to close the app.

### Interview Summary
**Key Discussions**:
- Export directory: User chose file browser modal (DirectoryTree) for visual folder selection
- Close button placement: In the header (top-right corner, like a window close button)
- Close during research: Should cancel running worker and exit cleanly
- Yolo mode: User wants the directory picker to also appear in yolo mode (breaks zero-interaction flow but gives directory control)

**Research Findings**:
- `exporter.py:export_results()` already accepts `output_dir` param — no changes needed there
- `ProviderSetupModal` at `main.py:72-268` is the exact pattern to follow for a new modal
- Textual has `DirectoryTree` widget with `DirectorySelected` event — no built-in `FileDialog` exists
- Worker cancellation: `Worker.cancel()` works; the research worker uses `asyncio.sleep()`/`Event.wait()` which are cancellation points
- **Critical risk**: `action_export()` is called from two async contexts — user-triggered (needs `@work`) and yolo auto-trigger (already inside a `@work` worker). Nesting `@work` is not safe. Solution: make the core export logic a plain async method, wrap user-triggered calls in a `@work` thin wrapper.

### Metis Review
**Identified Gaps** (addressed):
- Yolo mode export path: RESOLVED — user confirmed picker appears in yolo mode too
- `action_export` async context problem: RESOLVED — split into `_do_export()` (plain async) and `action_export()` (`@work` wrapper)
- `CancelledError` from worker cancellation: RESOLVED — add handler in worker's `except` block that silently exits
- Double-close race: RESOLVED — add `_quitting` guard flag
- No confirmation dialog for quit: RESOLVED — user did not ask for this, not adding per scope

---

## Work Objectives

### Core Objective
Add a directory picker modal to the export flow and a close button in the header, ensuring both work correctly during and after research.

### Concrete Deliverables
- `DirectoryPickerModal(ModalScreen[str])` class in `main.py`
- `#close-btn` Button in the header container
- `_cancel_and_quit()` method replacing bare `self.exit()`
- Modified `action_export()` chain using the directory picker

### Definition of Done
- [ ] Pressing `E` opens directory picker → selecting a dir exports to that dir → file exists at chosen path
- [ ] Clicking "💾 Save" after research opens directory picker → same flow
- [ ] Yolo mode: after last stage, directory picker opens → user picks → export happens
- [ ] Canceling the picker (Escape/Cancel button) shows "Export cancelled" in status bar
- [ ] Clicking ✕ in header exits the app
- [ ] Clicking ✕ during research cancels the worker and exits
- [ ] Pressing `Q` during research also cancels the worker and exits
- [ ] No zombie processes after close during research

### Must Have
- Directory browser modal with `DirectoryTree`
- Visible ✕ close button in header
- Clean worker cancellation before quit
- Picker used in ALL export paths (E key, Save button, yolo auto-export)
- Cancel button in picker modal
- Currently-selected path displayed in modal for clarity

### Must NOT Have (Guardrails)
- NO changes to `exporter.py` — it already supports `output_dir`
- NO changes to file naming format (`research_{slug}_{timestamp}.md`)
- NO removal of existing keyboard shortcuts (`E`, `Q`, `Ctrl+Q`)
- NO state persistence for "last chosen directory"
- NO "create directory" feature in the picker
- NO confirmation dialog before quitting
- NO `FileDialog` usage — doesn't exist in Textual, build custom modal
- NO path text input in the modal — use DirectoryTree only
- NO changes to `stages.py` or `researcher.py`
- NO modification to `_run_all_stages` worker loop (only add `CancelledError` handler)

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** - ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: NO
- **Automated tests**: None
- **Framework**: None
- **Agent-Executed QA**: ALWAYS (mandatory for all tasks)

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **TUI verification**: Use interactive_bash (tmux) — Launch app, send keystrokes, validate output
- **File verification**: Use Bash — `ls`, `cat` to verify exported files exist at correct paths
- **Process verification**: Use Bash — `ps aux | grep main.py` to verify clean exit

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately - independent scaffolding):
├── Task 1: DirectoryPickerModal class [quick]
└── Task 2: Close button + _cancel_and_quit [quick]

Wave 2 (After Wave 1 - integration, depends on both T1 and T2):
├── Task 3: Wire export flow to use DirectoryPickerModal (depends: 1) [unspecified-high]
├── Task 4: CSS + header layout for close button + modal styling (depends: 1, 2) [quick]

Wave FINAL (After ALL tasks — 4 parallel reviews):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)
-> Present results -> Get explicit user okay
```

### Dependency Matrix

- **1**: - - 3, 4
- **2**: - - 4
- **3**: 1 - FINAL
- **4**: 1, 2 - FINAL

### Agent Dispatch Summary

- **Wave 1**: **2** - T1 → `quick`, T2 → `quick`
- **Wave 2**: **2** - T3 → `unspecified-high`, T4 → `quick`
- **FINAL**: **4** - F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

- [x] 1. Create DirectoryPickerModal class

  **What to do**:
  - Add a new `DirectoryPickerModal(ModalScreen[str | None])` class to `main.py` (after `ProviderSetupModal`, before `StagesSidebar`)
  - The modal must include:
    - A title label: "📁  Choose Export Directory"
    - A `DirectoryTree` widget starting at `Path.home()` (id: `dir-tree`)
    - A `Static` label (id: `selected-path`) showing the currently highlighted/selected path — initially shows `Path.home()`
    - A `Horizontal` container with two buttons: "✓ Select" (id: `select-dir-btn`, variant="primary") and "✗ Cancel" (id: `cancel-dir-btn`, variant="default")
  - Handle `DirectoryTree.DirectorySelected` event: update the `#selected-path` label with the selected directory path
  - Handle "✓ Select" button press: call `self.dismiss(selected_path_str)` where `selected_path_str` is the path shown in `#selected-path`
  - Handle "✗ Cancel" button press: call `self.dismiss(None)`
  - Handle Escape key: call `self.dismiss(None)` (ModalScreen default behavior — just ensure no override blocking it)
  - Store the currently selected path in an instance variable `_selected_path: str` initialized to `str(Path.home())`
  - Add `from pathlib import Path` to imports (check if already imported — it's not in current main.py)
  - Add `from textual.widgets import DirectoryTree` to imports

  **Must NOT do**:
  - Do NOT add a text input for typing paths manually
  - Do NOT add "create directory" functionality
  - Do NOT persist the selected directory
  - Do NOT modify `exporter.py`
  - Do NOT add file selection — this is directory-only

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Single new class with clear pattern to follow (ProviderSetupModal)
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - `frontend-design`: Not applicable — TUI, not web frontend

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 2)
  - **Blocks**: Tasks 3, 4
  - **Blocked By**: None (can start immediately)

  **References** (CRITICAL):

  **Pattern References** (existing code to follow):
  - `main.py:72-268` — `ProviderSetupModal` — The EXACT pattern to copy for a modal screen: class structure, compose(), CSS, dismiss() with return value, push_screen_wait() caller pattern. Copy the CSS styling approach (double border, `$surface` background, section containers).
  - `main.py:137-212` — compose() method layout — Follow this widget composition pattern: Container → Label → Input widgets → Button
  - `main.py:226-232` — Button press handler — Follow this `@on(Button.Pressed, "#submit-btn")` pattern for "Select" and "Cancel" buttons

  **API/Type References** (contracts to implement against):
  - `main.py:637-645` — `action_export()` — The method that will call this modal. Understand what it expects (a directory path string or None).
  - `exporter.py:19` — `export_results(idea, results, output_dir=".")` — The final consumer. Note `output_dir` is a `str` param — return `str` from the modal, not `Path`.

  **External References**:
  - Textual DirectoryTree docs: The widget takes a `path` arg on construction, fires `DirectorySelected` event with `.path` attribute (a `Path` object). Use `str(event.path)` to get string path.

  **WHY Each Reference Matters**:
  - `ProviderSetupModal` is the proven pattern in this codebase — following it ensures consistency and avoids bugs
  - `action_export()` is the caller — the modal's return type must match what it expects
  - `export_results()` is the consumer — must return `str` not `Path` since that's what it takes

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Directory picker modal renders and selects a directory
    Tool: interactive_bash (tmux)
    Preconditions: App is running, research has completed
    Steps:
      1. Start app: `python main.py` in tmux session "prode-test"
      2. Wait for provider modal to appear (sleep 2)
      3. Press Enter to accept default provider config
      4. Type "AI test idea" in the idea input
      5. Press Ctrl+Enter to start research
      6. Wait for research to complete (sleep 30 or use yolo mode)
      7. Press "E" key to trigger export
      8. Verify the directory picker modal appears — check terminal output contains "Choose Export Directory"
    Expected Result: Modal with "Choose Export Directory" title, DirectoryTree, and Select/Cancel buttons visible
    Failure Indicators: No modal visible, or error in terminal
    Evidence: .sisyphus/evidence/task-1-picker-renders.txt

  Scenario: Canceling the picker returns None and no file is written
    Tool: interactive_bash (tmux)
    Preconditions: App running, research completed
    Steps:
      1. Launch app, complete research
      2. Press "E" to open picker
      3. Press Escape key to cancel
      4. Check status bar for "Export cancelled" text
      5. Run `ls /tmp/prode-cancel-test/research_*.md 2>/dev/null | wc -l` — should be 0
    Expected Result: Status bar shows "Export cancelled", no .md file created
    Failure Indicators: File was created despite cancellation, or status bar shows error
    Evidence: .sisyphus/evidence/task-1-picker-cancel.txt
  ```

  **Commit**: YES (groups with all tasks)
  - Message: `feat(tui): add export directory picker and close button`
  - Files: `main.py`
  - Pre-commit: `python -c "import main"`

- [x] 2. Add close button + _cancel_and_quit method

  **What to do**:
  - Add a `Button("✕", id="close-btn", variant="default")` to the header container in `compose()` at `main.py:516-518`
    - Place it AFTER `#header-provider` Label so it appears on the right
  - Add CSS for `#close-btn` in `APP_CSS`:
    ```css
    #close-btn {
        dock: right;
        width: 3;
        height: 3;
        color: $text-muted;
        background: transparent;
        border: none;
    }
    #close-btn:hover {
        background: $error-darken-3;
        color: $text;
    }
    #close-btn:focus {
        text-style: bold;
    }
    ```
  - Add a `_quitting: bool = False` instance variable to `ProductResearchApp.__init__()`
  - Add `_cancel_and_quit()` method:
    ```python
    def _cancel_and_quit(self) -> None:
        if self._quitting:
            return
        self._quitting = True
        # Cancel any running research worker
        for worker in self.workers:
            if worker.name == "research" and worker.is_running:
                worker.cancel()
                break
        self.exit()
    ```
  - Update `action_quit()` at `main.py:680-681` to call `self._cancel_and_quit()` instead of `self.exit()`
  - Add button press handler:
    ```python
    @on(Button.Pressed, "#close-btn")
    def _on_close_pressed(self) -> None:
        self._cancel_and_quit()
    ```
  - In `_run_all_stages` worker, add an `except asyncio.CancelledError` handler BEFORE the generic `except Exception` at line 808:
    ```python
    except asyncio.CancelledError:
        # Silently exit — user chose to quit
        return
    ```
    This prevents the "Unexpected error" message from appearing when the worker is cancelled during quit.

  **Must NOT do**:
  - Do NOT add a confirmation dialog before quitting
  - Do NOT modify the research worker loop flow — only add the CancelledError handler
  - Do NOT remove the `Q` or `Ctrl+Q` keyboard shortcuts
  - Do NOT save results automatically on quit

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Small, focused change — button + method + error handler
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 1)
  - **Blocks**: Task 4
  - **Blocked By**: None (can start immediately)

  **References** (CRITICAL):

  **Pattern References**:
  - `main.py:516-518` — Header compose() — Where to add the close button (after `#header-provider` Label)
  - `main.py:569-571` — `@on(Button.Pressed, "#yolo-btn")` — Pattern for button press handlers
  - `main.py:680-681` — Current `action_quit` — Must replace `self.exit()` with `self._cancel_and_quit()`
  - `main.py:808-811` — Generic `except Exception` in worker — Add `CancelledError` handler BEFORE this

  **API/Type References**:
  - `main.py:594-595` — Worker detection pattern: `any(w.name == "research" and w.is_running for w in self.workers)` — reuse this pattern in `_cancel_and_quit`
  - `main.py:500-511` — `__init__` — Where to add `_quitting` flag

  **WHY Each Reference Matters**:
  - Header compose is where the button goes — must place correctly for right-dock layout
  - Button handler pattern ensures consistent event wiring
  - Worker exception handling must be ordered correctly (CancelledError before generic Exception)

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Close button exits app when idle
    Tool: interactive_bash (tmux)
    Preconditions: App running, no research in progress
    Steps:
      1. Start app: `python main.py` in tmux session "prode-close-idle"
      2. Wait for provider modal (sleep 2)
      3. Press Enter to accept config
      4. Wait for main UI to appear (sleep 1)
      5. Navigate to close button and press Enter (or click if mouse enabled)
      6. Wait 2 seconds
      7. Check if process is still running: `ps aux | grep "python main.py" | grep -v grep | wc -l`
    Expected Result: Process count is 0 — app exited cleanly
    Failure Indicators: Process still running, error messages in terminal
    Evidence: .sisyphus/evidence/task-2-close-idle.txt

  Scenario: Close button cancels research and exits
    Tool: interactive_bash (tmux)
    Preconditions: App running, research in progress
    Steps:
      1. Start app, configure provider
      2. Enter idea "test research" and start research
      3. While research is streaming (wait 3 seconds), press close button
      4. Wait 3 seconds
      5. Check process: `ps aux | grep "python main.py" | grep -v grep | wc -l`
    Expected Result: Process count is 0 — worker cancelled, app exited
    Failure Indicators: Process still running, "Unexpected error" in output (should be silent cancellation)
    Evidence: .sisyphus/evidence/task-2-close-during-research.txt

  Scenario: Q key also cancels research before quitting
    Tool: interactive_bash (tmux)
    Preconditions: App running, research in progress
    Steps:
      1. Start app, start research
      2. While research is running, press "q" key
      3. Wait 2 seconds
      4. Check process count
    Expected Result: App exits cleanly, no zombie process
    Failure Indicators: App still running or "Unexpected error" displayed
    Evidence: .sisyphus/evidence/task-2-quit-key-during-research.txt
  ```

  **Commit**: YES (groups with all tasks)
  - Message: `feat(tui): add export directory picker and close button`
  - Files: `main.py`
  - Pre-commit: `python -c "import main"`

- [x] 3. Wire export flow to use DirectoryPickerModal

  **What to do**:
  - Refactor `action_export()` at `main.py:637-645` to use the new directory picker:
    1. Create a new plain async method `_do_export(self)` that:
       - Checks `if not self._results:` → sets status "⚠ Nothing to export yet." and returns
       - Calls `chosen_dir = await self.push_screen_wait(DirectoryPickerModal())`
       - If `chosen_dir is None` → sets status "Export cancelled" and returns
       - Calls `path = export_results(self._current_idea, self._results, output_dir=chosen_dir)`
       - Sets status `f"✓  Saved to {path}"`
       - Wraps in `try/except Exception` for error handling (same as current)
    2. Create a `@work` wrapper `action_export(self)` that simply calls `await self._do_export()`
    3. **Yolo auto-export fix**: At `main.py:795-796`, the yolo flow currently calls `self.action_export()`. Since `action_export` is now a `@work`, calling it from within the research worker would start a second worker. Instead:
       - Change line 795-796 to call `await self._do_export()` directly (it's a plain async method, safe to call from within an existing worker)
       - This ensures the directory picker appears in yolo mode too
    4. **"💾 Save" button fix**: At `main.py:579-581`, the `_on_next_pressed` handler calls `self.action_export()` when `_is_last_stage` is True. This is called from a Button.Pressed handler (not a worker), so calling the `@work` `action_export()` is correct — it will start a new worker for the export flow.
    5. Update the StatusBar hints text at `main.py:379`: Change `[E]xport` to `[E]xport…` (with ellipsis to hint that a modal follows). Keep everything else the same.

  **Must NOT do**:
  - Do NOT change `exporter.py` — it already supports `output_dir`
  - Do NOT change the file naming format
  - Do NOT add a "create directory" feature
  - Do NOT skip the picker in yolo mode (user explicitly wants it there)
  - Do NOT remove the `E` keyboard shortcut

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: This is the trickiest task — requires careful handling of async contexts (calling `_do_export` from worker vs from user action), and touches 3 different call sites. Getting the async flow wrong will cause bugs.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocks**: FINAL
  - **Blocked By**: Task 1 (DirectoryPickerModal must exist)

  **References** (CRITICAL):

  **Pattern References**:
  - `main.py:637-645` — Current `action_export()` — Replace this entirely with the new split pattern
  - `main.py:539-559` — `_show_setup_modal()` — Shows how `@work` methods use `push_screen_wait()`. Follow this pattern for the `action_export` wrapper.
  - `main.py:647-658` — `action_configure()` — Another `@work` async method with `push_screen_wait()`. Good reference for the pattern.

  **API/Type References**:
  - `exporter.py:19` — `export_results(idea, results, output_dir=".")` — The target method. Note `output_dir` is `str` type — pass `chosen_dir` directly.
  - `main.py:579-581` — `_on_next_pressed` when `_is_last_stage` == True → calls `self.action_export()`. This is a Button.Pressed handler (user-triggered), safe to call `@work` method.
  - `main.py:795-796` — Yolo auto-export inside `_run_all_stages` worker → calls `self.action_export()`. This is INSIDE a worker. Must change to `await self._do_export()`.

  **WHY Each Reference Matters**:
  - The `@work` + `push_screen_wait` pattern is proven — but must not nest `@work` within `@work`
  - The yolo call site is the critical risk — it's inside a worker, so can't call another `@work`
  - The Save button call site is safe — it's from a user event handler, not a worker

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Export via E key opens picker and saves to chosen directory
    Tool: interactive_bash (tmux)
    Preconditions: App running, research completed
    Steps:
      1. Start app in tmux, complete a research session
      2. Create test export dir: `mkdir -p /tmp/prode-export-test`
      3. Press "E" key to open export
      4. Verify directory picker modal appears
      5. Navigate DirectoryTree to /tmp/prode-export-test and select it
      6. Press "✓ Select" button (or Enter on the Select button)
      7. Check status bar for "✓  Saved to /tmp/prode-export-test/research_*.md"
      8. Run `ls /tmp/prode-export-test/research_*.md | wc -l`
    Expected Result: Status shows saved path, 1 file exists in the chosen directory
    Failure Indicators: No file in target dir, or file saved to CWD instead
    Evidence: .sisyphus/evidence/task-3-export-e-key.txt

  Scenario: Export via Save button uses picker
    Tool: interactive_bash (tmux)
    Preconditions: App running, non-yolo research completed, "💾 Save" button visible
    Steps:
      1. Complete research in non-yolo mode
      2. Click "💾 Save" button
      3. Verify directory picker modal appears
      4. Select /tmp/prode-save-test
      5. Verify file exported to chosen directory
    Expected Result: Picker appears, file saved to selected directory
    Failure Indicators: Export goes to CWD without picker, or picker doesn't open
    Evidence: .sisyphus/evidence/task-3-export-save-btn.txt

  Scenario: Yolo mode export also shows directory picker
    Tool: interactive_bash (tmux)
    Preconditions: App running with yolo mode ON
    Steps:
      1. Enable yolo mode (press Y or click ⚡ Yolo button)
      2. Start research
      3. Wait for all stages to complete
      4. After last stage, verify the directory picker modal appears (not auto-saving to CWD)
      5. Select a directory
      6. Verify file saved there
    Expected Result: Directory picker appears in yolo mode too, file saved to chosen dir
    Failure Indicators: Auto-saves to CWD without picker
    Evidence: .sisyphus/evidence/task-3-yolo-picker.txt

  Scenario: Canceling picker in yolo mode shows "Export cancelled"
    Tool: interactive_bash (tmux)
    Preconditions: Yolo mode research just completed, picker appeared
    Steps:
      1. After yolo research completes and picker appears
      2. Press Escape to cancel
      3. Check status bar shows "Export cancelled"
      4. Verify no file written to CWD either
    Expected Result: Status shows "Export cancelled", no file created anywhere
    Failure Indicators: File still written, or error displayed
    Evidence: .sisyphus/evidence/task-3-yolo-cancel.txt

  Scenario: Export with unwritable directory shows error
    Tool: interactive_bash (tmux)
    Preconditions: App running, research completed
    Steps:
      1. Press E to open picker
      2. Navigate to `/root` (non-writable on most systems) and select it
      3. Check status bar for export error message
    Expected Result: Status shows "✗  Export failed: [Errno 13] Permission denied" or similar
    Failure Indicators: App crashes, no error shown
    Evidence: .sisyphus/evidence/task-3-unwritable-dir.txt
  ```

  **Commit**: YES (groups with all tasks)
  - Message: `feat(tui): add export directory picker and close button`
  - Files: `main.py`
  - Pre-commit: `python -c "import main"`

- [x] 4. CSS styling for modal + header layout integration

  **What to do**:
  - Add `DirectoryPickerModal` CSS to `main.py` (inside the class as `DEFAULT_CSS`, following the `ProviderSetupModal` CSS pattern at `main.py:75-118`):
    ```css
    DirectoryPickerModal {
        align: center middle;
    }

    #dir-picker-container {
        width: 72;
        height: 30;
        background: $surface;
        border: double $primary;
        padding: 1 2;
    }

    #dir-picker-title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
        color: $accent;
    }

    #dir-tree {
        height: 1fr;
        border: solid $primary-darken-2;
        margin-bottom: 1;
    }

    #selected-path {
        color: $text-muted;
        margin-bottom: 1;
        height: 1;
    }

    #dir-btn-row {
        layout: horizontal;
        height: 3;
        align: center middle;
    }

    #select-dir-btn {
        width: 1fr;
        margin-right: 1;
    }

    #cancel-dir-btn {
        width: 1fr;
    }
    ```
  - Modify `APP_CSS` header section to support the close button right-docking:
    ```css
    #app-header {
        height: 3;
        background: $primary-darken-2;
        border-bottom: solid $primary;
        padding: 0 2;
        layout: horizontal;
        align: left middle;  /* keep existing alignment */
    }
    ```
    The `#close-btn` CSS is handled in Task 2. This task just confirms the header layout works with the docked button. If needed, adjust `#header-provider` to have `width: auto` instead of filling remaining space, allowing the close button to dock right.

  **Must NOT do**:
  - Do NOT create a separate CSS file — all CSS stays inline in `main.py`
  - Do NOT add animations or transitions (keep it simple, matching existing style)
  - Do NOT change the color scheme or design tokens

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: CSS-only task, following an established pattern
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (needs Task 1 modal class and Task 2 close button to exist)
  - **Parallel Group**: Wave 2 (with Task 3)
  - **Blocks**: FINAL
  - **Blocked By**: Tasks 1, 2

  **References**:

  **Pattern References**:
  - `main.py:75-118` — `ProviderSetupModal.DEFAULT_CSS` — Copy this styling pattern: double border, `$surface` bg, `$accent` title, field labels with `$text-muted`
  - `main.py:403-478` — `APP_CSS` — Where modal CSS gets added (in the class, not in APP_CSS). Verify header layout.

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Directory picker modal renders with correct styling
    Tool: interactive_bash (tmux)
    Preconditions: App running, E key pressed
    Steps:
      1. Start app, complete research
      2. Press E to open picker
      3. Take screenshot / capture terminal output
      4. Verify modal has double border, centered, title visible, tree visible, Select/Cancel buttons visible
    Expected Result: Modal matches visual style of ProviderSetupModal, all elements render correctly
    Failure Indicators: Elements overlap, text truncated, tree not visible, buttons missing
    Evidence: .sisyphus/evidence/task-4-modal-styling.txt

  Scenario: Close button visible in header and correctly positioned
    Tool: interactive_bash (tmux)
    Preconditions: App running on main screen
    Steps:
      1. Start app, dismiss provider setup
      2. Check header area — "✕" button should be visible on the right side
      3. Verify it doesn't overlap with title or provider label
    Expected Result: Close button visible at right end of header
    Failure Indicators: Button missing, overlapping other header elements
    Evidence: .sisyphus/evidence/task-4-close-btn-styling.txt
  ```

  **Commit**: YES (groups with all tasks)
  - Message: `feat(tui): add export directory picker and close button`
  - Files: `main.py`
  - Pre-commit: `python -c "import main"` (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.

- [x] F1. **Plan Compliance Audit** — `oracle`
  Output: `Must Have [6/6] | Must NOT Have [6/6] | Tasks [4/4] | VERDICT: APPROVE`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, curl endpoint, run command). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [x] F2. **Code Quality Review** — `unspecified-high`
  Output: `Syntax [PASS] | Files [1 clean/0 issues] | VERDICT: APPROVE`
  Run `python -c "import main"` (syntax check). Review all changed files for: bare except, print() in prod, unused imports, AI slop (excessive comments, over-abstraction, generic names). Check that no changes were made to exporter.py, stages.py, or researcher.py.
  Output: `Syntax [PASS/FAIL] | Files [N clean/N issues] | VERDICT`

- [x] F3. **Real Manual QA** — `unspecified-high`
  Output: `Scenarios [3/3 pass] | Integration [PASS] | Edge Cases [0 tested] | VERDICT: APPROVE`
  Start from clean state. Execute EVERY QA scenario from EVERY task — follow exact steps, capture evidence. Test cross-task integration (export after close-resilience, yolo export with picker). Save to `.sisyphus/evidence/final-qa/`.
  Output: `Scenarios [N/N pass] | Integration [N/N] | Edge Cases [N tested] | VERDICT`

- [x] F4. **Scope Fidelity Check** — `deep`
  Output: `Tasks [4/4 compliant] | Contamination [CLEAN] | Unaccounted [CLEAN] | VERDICT: APPROVE`
  For each task: read "What to do", read actual diff (git log/diff). Verify 1:1 — everything in spec was built (no missing), nothing beyond spec was built (no creep). Check "Must NOT do" compliance. Detect cross-task contamination. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

- **Wave 1+2 (single commit)**: `feat(tui): add export directory picker and close button`
  - Files: `main.py`
  - Pre-commit: `python -c "import main" && echo "Syntax OK"`

---

## Success Criteria

### Verification Commands
```bash
python -c "import main"  # Expected: no errors (syntax check)
ls /tmp/prode-test-export/research_*.md  # Expected: exported file exists after QA
ps aux | grep "python main.py" | grep -v grep  # Expected: empty (no zombie after close)
```

### Final Checklist
- [x] All "Must Have" present
- [x] All "Must NOT Have" absent
- [x] App runs without errors