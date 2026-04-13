#!/usr/bin/env python3
"""
AI Product Research Tool
Terminal TUI powered by Textual + Anthropic/Ollama + Web Search
"""

import asyncio
import os
from pathlib import Path
from typing import Dict, Optional

from dotenv import load_dotenv
from rich.markdown import Markdown as RichMarkdown
from rich.text import Text
from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    DirectoryTree,
    Input,
    Label,
    ProgressBar,
    RadioButton,
    RadioSet,
    Static,
    TextArea,
)
from textual.widget import Widget

from config import load_config, save_config
from exporter import export_results
from researcher import ProviderConfig, run_research_pipeline
from stages import STAGES

load_dotenv()

VERSION = "v1.0.0"
SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
RATE_LIMIT_WAIT = 5


def _extract_port(base_url: str) -> str:
    """Extract port number from a base_url like 'http://localhost:8080/v1'."""
    from urllib.parse import urlparse

    parsed = urlparse(base_url)
    return str(parsed.port) if parsed.port else "11434"


class IdeaInput(TextArea):
    DEFAULT_CSS = """
    IdeaInput {
        border: round $primary;
        padding: 0 1;
        background: $background;
    }
    IdeaInput .text-area--gutter {
        display: none;
    }
    """

    def __init__(self) -> None:
        super().__init__(id="idea-input")


# ─── Provider setup modal ─────────────────────────────────────────────────────


class ProviderSetupModal(ModalScreen[ProviderConfig]):
    """Startup modal: choose Anthropic, Ollama Local, or a custom endpoint."""

    DEFAULT_CSS = """
    ProviderSetupModal {
        align: center middle;
    }

    #modal-container {
        width: 68;
        height: auto;
        background: $surface;
        border: double $primary;
        padding: 2 4;
    }

    #modal-title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
        color: $accent;
    }

    #provider-radio {
        margin-bottom: 1;
    }

    .section {
        border: solid $primary-darken-2;
        padding: 1 2;
        margin-top: 1;
        margin-bottom: 1;
    }

    .field-label {
        color: $text-muted;
        margin-bottom: 0;
    }

    .field-input {
        margin-bottom: 1;
    }

    #submit-btn {
        width: 100%;
        margin-top: 1;
    }
    """

    def __init__(
        self, saved_config: Optional[ProviderConfig] = None, prefill_key: str = ""
    ) -> None:
        super().__init__()
        self._prefill_key = prefill_key
        self._provider_idx = 0
        self._saved_config = saved_config
        if saved_config:
            if saved_config.provider == "anthropic":
                self._provider_idx = 0
                self._prefill_key = saved_config.api_key or prefill_key
            elif saved_config.base_url and "localhost" in saved_config.base_url:
                self._provider_idx = 1
            else:
                self._provider_idx = 2

    def compose(self) -> ComposeResult:
        sc = self._saved_config
        with Container(id="modal-container"):
            yield Label("⚙  Configure AI Provider", id="modal-title")

            with RadioSet(id="provider-radio"):
                yield RadioButton(
                    "Anthropic  (claude-sonnet-4-6 + web search)",
                    value=self._provider_idx == 0,
                )
                yield RadioButton(
                    "Ollama Local  (localhost:11434)",
                    value=self._provider_idx == 1,
                )
                yield RadioButton(
                    "Ollama Cloud / Custom Endpoint",
                    value=self._provider_idx == 2,
                )

            with Container(id="anthropic-section", classes="section"):
                yield Label("Anthropic API Key", classes="field-label")
                yield Input(
                    value=self._prefill_key,
                    placeholder="sk-ant-...",
                    password=True,
                    id="ant-key",
                    classes="field-input",
                )

            with Container(id="ollama-local-section", classes="section"):
                yield Label("Model name", classes="field-label")
                yield Input(
                    value=(sc.model if sc and self._provider_idx == 1 else "llama3.2"),
                    placeholder="llama3.2",
                    id="ol-local-model",
                    classes="field-input",
                )
                yield Label("Port  (default 11434)", classes="field-label")
                yield Input(
                    value=(
                        _extract_port(sc.base_url)
                        if sc and self._provider_idx == 1 and sc.base_url
                        else "11434"
                    ),
                    placeholder="11434",
                    id="ol-local-port",
                    classes="field-input",
                )

            with Container(id="ollama-cloud-section", classes="section"):
                yield Label("Base URL", classes="field-label")
                yield Input(
                    value=(sc.base_url or "" if sc and self._provider_idx == 2 else ""),
                    placeholder="https://your-ollama-host.com",
                    id="ol-cloud-url",
                    classes="field-input",
                )
                yield Label("Model name", classes="field-label")
                yield Input(
                    value=(sc.model or "" if sc and self._provider_idx == 2 else ""),
                    placeholder="llama3.2",
                    id="ol-cloud-model",
                    classes="field-input",
                )
                yield Label(
                    "API Key  (leave blank if not required)", classes="field-label"
                )
                yield Input(
                    value=(sc.api_key or "" if sc and self._provider_idx == 2 else ""),
                    placeholder="(optional)",
                    password=True,
                    id="ol-cloud-key",
                    classes="field-input",
                )

            yield Button("Continue →", variant="primary", id="submit-btn")

    def on_mount(self) -> None:
        self.query_one("#anthropic-section").display = self._provider_idx == 0
        self.query_one("#ollama-local-section").display = self._provider_idx == 1
        self.query_one("#ollama-cloud-section").display = self._provider_idx == 2

    @on(RadioSet.Changed, "#provider-radio")
    def _on_provider_changed(self, event: RadioSet.Changed) -> None:
        self._provider_idx = event.index
        self.query_one("#anthropic-section").display = event.index == 0
        self.query_one("#ollama-local-section").display = event.index == 1
        self.query_one("#ollama-cloud-section").display = event.index == 2

    @on(Button.Pressed, "#submit-btn")
    def _submit(self) -> None:
        config = self._build_config()
        if config:
            save_config(config)
            self.dismiss(config)

    def _build_config(self) -> Optional[ProviderConfig]:
        idx = self._provider_idx

        if idx == 0:
            key = self.query_one("#ant-key", Input).value.strip()
            if not key:
                self.app.notify("Please enter an API key.", severity="warning")
                return None
            elif len(key) < 10:
                self.app.notify(
                    "API key seems too short — please check it.", severity="warning"
                )
                return None
            return ProviderConfig(provider="anthropic", api_key=key)

        if idx == 1:
            model = self.query_one("#ol-local-model", Input).value.strip() or "llama3.2"
            port = self.query_one("#ol-local-port", Input).value.strip() or "11434"
            return ProviderConfig(
                provider="ollama",
                model=model,
                base_url=f"http://localhost:{port}/v1",
            )

        # idx == 2
        url = self.query_one("#ol-cloud-url", Input).value.strip()
        model = self.query_one("#ol-cloud-model", Input).value.strip()
        key = self.query_one("#ol-cloud-key", Input).value.strip()
        if not url or not model:
            return None
        return ProviderConfig(
            provider="ollama",
            model=model,
            base_url=url,
            api_key=key or None,
        )

    def _get_model_name(self) -> str:
        """Return the model name from the modal's current inputs."""
        idx = self._provider_idx
        if idx == 0:
            return "claude-sonnet"
        if idx == 1:
            return self.query_one("#ol-local-model", Input).value.strip() or "llama3.2"
        return self.query_one("#ol-cloud-model", Input).value.strip() or "llama3.2"


# ─── Directory picker modal ───────────────────────────────────────────────────


class DirectoryPickerModal(ModalScreen[str | None]):
    """Modal for selecting a directory to export research results."""

    DEFAULT_CSS = """
    DirectoryPickerModal {
        align: center middle;
    }

    #dir-picker-container {
        width: 72;
        height: 26;
        background: $surface;
        border: double $primary;
        padding: 1 2;
    }

    #dir-picker-title {
        text-align: center;
        text-style: bold;
        height: 1;
        margin-bottom: 1;
        color: $accent;
    }

    #dir-tree {
        height: 13;
        max-height: 13;
        overflow-y: auto;
        border: solid $primary-darken-2;
    }

    #selected-path {
        height: 1;
        color: $text-muted;
    }

    #dir-btn-row {
        dock: bottom;
        height: 3;
        align: right middle;
        padding-top: 1;
    }

    #dir-btn-row > Button {
        margin-left: 1;
    }
    """

    BINDINGS = [
        ("enter", "confirm", "Export to this directory"),
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._selected_path: str = str(Path.home())

    def compose(self) -> ComposeResult:
        with Container(id="dir-picker-container"):
            yield Label("📁  Choose Export Directory", id="dir-picker-title")
            yield DirectoryTree(Path.home(), id="dir-tree")
            yield Static(f"Selected: {self._selected_path}", id="selected-path")
            with Horizontal(id="dir-btn-row"):
                yield Button("Cancel", variant="default", id="cancel-btn")
                yield Button("📂 Export", variant="success", id="select-btn")

    @on(DirectoryTree.DirectorySelected)
    def _on_directory_selected(self, event: DirectoryTree.DirectorySelected) -> None:
        self._selected_path = str(event.path)
        self.query_one("#selected-path", Static).update(
            f"Selected: {self._selected_path}"
        )

    @on(Button.Pressed, "#select-btn")
    def _on_select(self) -> None:
        self.dismiss(self._selected_path)

    @on(Button.Pressed, "#cancel-btn")
    def _on_cancel(self) -> None:
        self.dismiss(None)

    def action_confirm(self) -> None:
        self.dismiss(self._selected_path)

    def action_cancel(self) -> None:
        self.dismiss(None)


class ExportSuccessModal(ModalScreen[bool]):
    """Modal shown after successful export. Returns True for New Session, False for Close."""

    DEFAULT_CSS = """
    ExportSuccessModal {
        align: center middle;
    }

    #export-success-container {
        width: 60;
        height: auto;
        background: $surface;
        border: double $primary;
        padding: 2 4;
    }

    #export-success-title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
        color: $accent;
    }

    #export-success-path {
        color: $text-muted;
        text-align: center;
        margin-bottom: 1;
    }

    #export-btn-row {
        align: center middle;
        height: 3;
    }

    #export-btn-row > Button {
        margin-left: 1;
        margin-right: 1;
    }
    """

    BINDINGS = [
        ("escape", "close_modal", "Close"),
    ]

    def __init__(self, path: str) -> None:
        super().__init__()
        self._path = path

    def compose(self) -> ComposeResult:
        with Container(id="export-success-container"):
            yield Label("✓  Report exported successfully!", id="export-success-title")
            yield Label(f"📄  {self._path}", id="export-success-path")
            with Horizontal(id="export-btn-row"):
                yield Button("Close", variant="default", id="export-close-btn")
                yield Button(
                    "🔄  New Session", variant="primary", id="export-new-session-btn"
                )

    @on(Button.Pressed, "#export-close-btn")
    def _on_close(self) -> None:
        self.dismiss(False)

    @on(Button.Pressed, "#export-new-session-btn")
    def _on_new_session(self) -> None:
        self.dismiss(True)

    def action_close_modal(self) -> None:
        self.dismiss(False)


# ─── Stages sidebar ───────────────────────────────────────────────────────────


class StagesSidebar(Widget):
    """Left sidebar listing all research stages with live status icons."""

    DEFAULT_CSS = """
    StagesSidebar {
        width: 20;
        border-right: solid $primary-darken-2;
        padding: 1 1;
        background: $panel;
    }
    """

    _spinner_idx: reactive[int] = reactive(0)

    def __init__(self) -> None:
        super().__init__()
        self._statuses: Dict[str, str] = {s.id: "pending" for s in STAGES}

    def on_mount(self) -> None:
        self.set_interval(0.1, self._tick)

    def _tick(self) -> None:
        if any(v == "running" for v in self._statuses.values()):
            self._spinner_idx = (self._spinner_idx + 1) % len(SPINNER_FRAMES)

    def watch__spinner_idx(self, _: int) -> None:  # noqa: N802
        self.refresh()

    def set_status(self, stage_id: str, status: str) -> None:
        self._statuses[stage_id] = status
        self.refresh()

    def set_score(self, stage_id: str, score: float) -> None:
        """Store quality score for a completed stage (0.0–1.0)."""
        if not hasattr(self, "_scores"):
            self._scores: dict[str, float] = {}
        self._scores[stage_id] = score
        self.refresh()

    def reset(self) -> None:
        self._statuses = {s.id: "pending" for s in STAGES}
        self.refresh()

    def render(self) -> Text:
        t = Text()
        t.append("STAGES\n\n", style="bold white")
        for stage in STAGES:
            status = self._statuses.get(stage.id, "pending")
            if status == "pending":
                icon, style = "○", "dim"
            elif status == "running":
                icon = SPINNER_FRAMES[self._spinner_idx]
                style = "bold yellow"
            elif status == "done":
                icon, style = "✓", "green"
            else:
                icon, style = "✗", "red"
            t.append(f"  {icon} ", style=style)
            t.append(f"{stage.short_name}\n", style=style)
        return t


# ─── Status bar ───────────────────────────────────────────────────────────────


class StatusBar(Widget):
    """Bottom bar: progress + live status message + key hints."""

    DEFAULT_CSS = """
    StatusBar {
        height: 5;
        dock: bottom;
        border-top: wide $primary;
        padding: 1 2;
        background: $surface-darken-1;
    }

    #progress-row {
        layout: horizontal;
        height: 2;
        align: left middle;
    }

    #bar {
        width: 28;
        margin-right: 2;
    }

    #stage-label {
        width: 1fr;
        color: $text;
        text-style: bold;
    }

    #hint-row {
        height: 1;
    }

    #hints {
        color: $text;
        text-style: bold;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(id="progress-row"):
            yield ProgressBar(total=len(STAGES), show_eta=False, id="bar")
            yield Label(
                "Ready — enter a product idea above.", id="stage-label", markup=False
            )
        with Container(id="hint-row"):
            yield Label(
                "[E]xport…  [C]onfigure  [Y]olo  [Q]uit  [Tab] focus  [↑↓] scroll",
                id="hints",
                markup=False,
            )

    def set_status(self, text: str) -> None:
        try:
            self.query_one("#stage-label", Label).update(text)
        except Exception:  # noqa: BLE001 — widget may not exist yet
            pass

    def set_progress(self, done: int) -> None:
        try:
            self.query_one("#bar", ProgressBar).progress = done
        except Exception:  # noqa: BLE001 — widget may not exist yet
            pass

    def reset(self) -> None:
        self.set_progress(0)
        self.set_status("Ready — enter a product idea above.")


# ─── Main App ─────────────────────────────────────────────────────────────────

APP_CSS = """
Screen {
    layout: vertical;
    background: $background;
}

#app-header {
    height: 3;
    background: $primary-darken-2;
    border-bottom: solid $primary;
    padding: 0 2;
    layout: horizontal;
    align: left middle;
}

#header-title {
    width: 1fr;
    text-style: bold;
    color: $accent;
}

#header-provider {
    color: $text-muted;
}

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

#input-section {
    height: 9;
    background: $panel;
    border-bottom: solid $primary-darken-2;
    padding: 1 2;
    layout: horizontal;
    align: left middle;
}

#idea-label {
    width: auto;
    margin-right: 1;
    color: $text-muted;
}

#idea-input {
    width: 1fr;
    height: 1fr;
    margin-right: 2;
}

#run-btn {
    width: 20;
}

#next-btn {
    width: 20;
    display: none;
}

#yolo-btn {
    width: 18;
}

#main-area {
    layout: horizontal;
    height: 1fr;
}

#output-scroll {
    width: 1fr;
    height: 1fr;
    overflow-y: auto;
    padding: 1 2;
    background: $background;
}

#output-md {
    width: 1fr;
}
"""


class ProductResearchApp(App):
    """AI Product Research TUI."""

    CSS = APP_CSS
    TITLE = "AI Product Research"

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", show=False),
        Binding("q", "quit", "Quit", show=False),
        Binding("e", "export", "Export"),
        Binding("c", "configure", "Configure"),
        Binding("y", "toggle_yolo", "Yolo"),
        Binding("tab", "toggle_focus", "Toggle focus"),
        Binding("ctrl+enter", "run_research", "Run", show=False, priority=True),
        Binding("n", "advance_stage", "Next stage"),
    ]

    _yolo_mode: reactive[bool] = reactive(False)

    def __init__(self) -> None:
        super().__init__()
        self._config: Optional[ProviderConfig] = None
        self._results: Dict[str, str] = {}
        self._current_idea: str = ""
        self._running: bool = False
        self._output_buffer: str = ""  # full accumulated text (for export)
        self._stage_buffer: str = ""  # current stage only (for live display)
        self._pending_refresh: bool = False
        self._last_flush_time: float = 0.0
        self._advance_event: asyncio.Event | None = None
        self._is_last_stage: bool = False
        self._quitting: bool = False

    # ── Layout ────────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        with Container(id="app-header"):
            yield Label("🔭  Prode  — Research before you build", id="header-title")
            yield Label(VERSION, id="header-provider")
            yield Button("✕", id="close-btn", variant="default")

        with Container(id="input-section"):
            yield Label("💡", id="idea-label")
            yield IdeaInput()
            yield Button("▶ Research", variant="primary", id="run-btn")
            yield Button("Next →", variant="success", id="next-btn")
            yield Button("⚡ Yolo: OFF", variant="default", id="yolo-btn")

        with Horizontal(id="main-area"):
            yield StagesSidebar()
            with Container(id="output-scroll"):
                yield Static("", id="output-md")

        yield StatusBar()

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def on_mount(self) -> None:
        self._show_setup_modal()

    @work
    async def _show_setup_modal(self) -> None:
        saved = load_config()
        if saved:
            self._config = saved
            self.query_one("#header-provider", Label).update(
                f"{VERSION}  ·  {saved.display_name}"
            )
            self.query_one("#idea-input", IdeaInput).focus()
            return

        prefill = os.environ.get("ANTHROPIC_API_KEY", "")
        config: Optional[ProviderConfig] = await self.push_screen_wait(
            ProviderSetupModal(prefill_key=prefill)
        )
        if config:
            self._config = config
            self.query_one("#header-provider", Label).update(
                f"{VERSION}  ·  {config.display_name}"
            )
        self.query_one("#idea-input", IdeaInput).focus()

    # ── Input handlers ────────────────────────────────────────────────────────

    @on(Button.Pressed, "#run-btn")
    def _on_run_pressed(self) -> None:
        run_btn = self.query_one("#run-btn", Button)
        run_btn.disabled = True
        self.action_run_research()

    @on(Button.Pressed, "#yolo-btn")
    def _on_yolo_pressed(self) -> None:
        self.action_toggle_yolo()

    @on(Button.Pressed, "#close-btn")
    def _on_close_pressed(self) -> None:
        self._cancel_and_quit()

    @on(Button.Pressed, "#next-btn")
    def _on_next_pressed(self) -> None:
        btn = self.query_one("#next-btn", Button)
        btn.disabled = True  # Guard against double-clicking
        btn.display = False
        btn.label = "Next →"
        if self._is_last_stage:
            self._is_last_stage = False
            self.action_export()
        else:
            if self._advance_event is not None:
                self._advance_event.set()

    # ── Actions ───────────────────────────────────────────────────────────────

    def action_advance_stage(self) -> None:
        if self._advance_event is not None:
            self._advance_event.set()

    def action_run_research(self) -> None:
        if self._running:
            # Auto-heal: if no worker is actually running, the flag is stale
            if not any(w.name == "research" and w.is_running for w in self.workers):
                self._running = False
            else:
                self.notify("Research already in progress…", severity="warning")
                return
        idea = self.query_one("#idea-input", IdeaInput).text.strip()
        if not idea:
            self.notify("Please enter a product idea first.", severity="error")
            self._set_status("⚠  Please enter a product idea first.")
            return
        if not self._config:
            self.notify(
                "No provider configured — please restart and set up a provider.",
                severity="error",
            )
            self._set_status("⚠  No provider configured.")
            return
        self._reset_session()
        self._current_idea = idea
        self._running = True
        self._output_buffer = f"# Product Research: {idea}\n\n"
        self._stage_buffer = f"# Product Research: {idea}\n\n"
        self._pending_refresh = False
        try:
            self.query_one("#output-md", Static).update(
                RichMarkdown(self._stage_buffer)
            )
        except Exception:  # noqa: BLE001 — widget may not exist yet
            pass
        display_idea = idea if len(idea) <= 50 else idea[:47] + "..."
        self.notify(f"Starting research for: {display_idea}", timeout=3)
        self._run_all_stages()

    # ------------------------------------------------------------------
    # Session reset — used by action_run_research and ExportSuccessModal
    # ------------------------------------------------------------------
    def _reset_session(self) -> None:
        """Clear all session state without starting a new pipeline."""
        self._results = {}
        self._current_idea = ""
        self._running = False
        self._is_last_stage = False
        self.query_one(StagesSidebar).reset()
        self.query_one(StatusBar).reset()
        try:
            btn = self.query_one("#next-btn", Button)
            btn.label = "Next →"
            btn.disabled = True
            btn.display = False
        except Exception:  # noqa: BLE001 — widget may not exist yet
            pass
        self._output_buffer = ""
        self._stage_buffer = ""
        try:
            self.query_one("#output-md", Static).update(RichMarkdown(""))
        except Exception:  # noqa: BLE001 — widget may not exist yet
            pass
        self.query_one("#idea-input", IdeaInput).text = ""
        self.query_one("#idea-input", IdeaInput).focus()
        self.query_one("#run-btn", Button).disabled = False

    async def _do_export(self) -> None:
        """Plain async method to perform export with directory picker."""
        if not self._results:
            self._set_status("⚠  Nothing to export yet.")
            return
        try:
            chosen_dir = await self.push_screen_wait(DirectoryPickerModal())
            if chosen_dir is None:
                self._set_status("Export cancelled")
                return
            path = export_results(
                self._current_idea, self._results, output_dir=chosen_dir
            )
            self._set_status(f"✓  Saved to {path}")
            new_session = await self.push_screen_wait(ExportSuccessModal(path=path))
            if new_session:
                self._reset_session()
        except Exception as exc:
            self._set_status(f"✗  Export failed: {exc}")

    @work
    async def action_export(self) -> None:
        """@work wrapper for user-triggered export (E key, Save button)."""
        await self._do_export()

    @work
    async def action_configure(self) -> None:
        saved = load_config()
        prefill = os.environ.get("ANTHROPIC_API_KEY", "")
        config: Optional[ProviderConfig] = await self.push_screen_wait(
            ProviderSetupModal(saved_config=saved, prefill_key=prefill)
        )
        if config:
            self._config = config
            self.query_one("#header-provider", Label).update(
                f"{VERSION}  ·  {config.display_name}"
            )

    def action_toggle_yolo(self) -> None:
        self._yolo_mode = not self._yolo_mode
        btn = self.query_one("#yolo-btn", Button)
        if self._yolo_mode:
            btn.label = "⚡ Yolo: ON"
            btn.variant = "warning"
            self.notify("Yolo mode ON — stages auto-advance", timeout=3)
        else:
            btn.label = "⚡ Yolo: OFF"
            btn.variant = "default"
            self.notify("Yolo mode OFF", timeout=2)

    def action_toggle_focus(self) -> None:
        inp = self.query_one("#idea-input", IdeaInput)
        scroll = self.query_one("#output-scroll")
        if inp.has_focus:
            scroll.focus()
        else:
            inp.focus()

    def _cancel_and_quit(self) -> None:
        if self._quitting:
            return
        self._quitting = True
        for worker in self.workers:
            if worker.name == "research" and worker.is_running:
                worker.cancel()
                break
        self.exit()

    def action_quit(self) -> None:
        self._cancel_and_quit()

    # ── Research worker ───────────────────────────────────────────────────────

    @work(name="research")
    async def _run_all_stages(self) -> None:
        """Run the full 8-stage research pipeline via Syrin REFLECTION."""
        try:
            sidebar = self.query_one(StagesSidebar)
            status_bar = self.query_one(StatusBar)
            self._advance_event = asyncio.Event()

            model_name = self._config.model or (
                "claude-sonnet" if self._config.provider == "anthropic" else "llama3.2"
            )

            async for event_type, payload in run_research_pipeline(
                idea=self._current_idea,
                provider=self._config.provider,
                model=model_name,
                api_key=self._config.api_key,
                base_url=self._config.base_url or None,
            ):
                if event_type == "stage_start":
                    stage_id = payload  # type: ignore[assignment]
                    stage = next(s for s in STAGES if s.id == stage_id)
                    sidebar.set_status(stage.id, "running")
                    status_bar.set_status(f"⟳  {stage.name}…")
                    self._output_buffer += f"\n\n## {stage.name}\n\n"
                    self._stage_buffer = f"## {stage.name}\n\n"

                elif event_type == "reflection_round":
                    stage_id, round_num = payload  # type: ignore[assignment]
                    stage = next(s for s in STAGES if s.id == stage_id)
                    self._stage_buffer += f"\n\n### Round {round_num + 1}\n\n"
                    status_bar.set_status(f"⟳  {stage.name} — Round {round_num + 1}…")

                elif event_type == "stage_complete":
                    result = payload  # type: ignore[assignment]
                    stage_text = result["content"]
                    rounds = result["rounds_completed"]
                    score = result.get("score")
                    stage_id = next(
                        (s.id for s in STAGES if s.id == stage_id),
                        next(s.id for s in STAGES if s.name in self._stage_buffer),
                    )
                    stage = next(s for s in STAGES if s.id == stage_id)

                    self._stage_buffer += stage_text
                    self._append_output(stage_text)
                    self._results[stage.id] = stage_text

                    score_str = f"{score:.0%}" if score is not None else "N/A"
                    sidebar.set_status(stage.id, "done")
                    sidebar.set_score(stage.id, score)

                    idx = STAGES.index(stage)
                    status_bar.set_progress(idx + 1)
                    await self._render_markdown()

                elif event_type == "error":
                    error_msg = payload  # type: ignore[assignment]
                    self._append_output(f"\n\n> ⚠ **{error_msg}**\n\n")
                    self.notify(
                        f"Error: {error_msg[:120]}", severity="error", timeout=10
                    )
                    sidebar.set_status(stage.id, "failed")

                elif event_type == "searching":
                    status_bar.set_status("🌐  Searching the web…")

                elif event_type == "search_done":
                    status_bar.set_status(f"⟳  {stage.name}…")

            # Pipeline complete — trigger export
            if self._yolo_mode:
                status_bar.set_status("✓  Research complete — saving automatically…")
                self.notify("Research complete! Exporting results…", timeout=4)
                await self._do_export()
            else:
                self._is_last_stage = True
                status_bar.set_status("✓  Research complete — click Save to export")
                self.notify("Research complete! Click Save to export.", timeout=5)

        except asyncio.CancelledError:
            self._append_output("\n\n> ✗ **Cancelled.**\n\n")
            self._set_status("✗  Cancelled")
            self.notify("Research cancelled.", severity="warning", timeout=5)

        except Exception as exc:
            self._append_output(f"\n\n> ✗ **Unexpected error:** {exc}\n\n")
            self._set_status(f"✗  Error: {exc}")
            self.notify(f"Unexpected error: {exc}", severity="error", timeout=15)

        finally:
            self._running = False
            run_btn = self.query_one("#run-btn", Button)
            run_btn.disabled = False
            if self._results:
                self._show_save_button()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _show_save_button(self):
        btn = self.query_one("#next-btn", Button)
        btn.label = "💾 Save"
        btn.display = True

    def _update_output(self, content: str) -> None:
        self._output_buffer = content
        try:
            self.query_one("#output-md", Static).update(RichMarkdown(content))
        except Exception:  # noqa: BLE001 — widget may not exist yet
            pass

    def _append_output(self, chunk: str) -> None:
        self._output_buffer += chunk
        self._stage_buffer += chunk
        if not self._pending_refresh:
            self._pending_refresh = True
            self.call_after_refresh(self._flush_output)

    def _flush_output(self) -> None:
        self._pending_refresh = False
        try:
            self.query_one("#output-md", Static).update(
                RichMarkdown(self._stage_buffer)
            )
            scroll = self.query_one("#output-scroll")
            if scroll.is_vertical_scroll_end:
                scroll.scroll_end(animate=False)
        except Exception:  # noqa: BLE001 — widget may not exist yet
            pass

    async def _render_markdown(self) -> None:
        """Parse markdown in a thread (non-blocking), then update the widget."""
        try:
            loop = asyncio.get_event_loop()
            rendered = await loop.run_in_executor(
                None, RichMarkdown, self._stage_buffer
            )
            self.query_one("#output-md", Static).update(rendered)
        except Exception:  # noqa: BLE001 — widget may not exist yet
            try:
                self.query_one("#output-md", Static).update(self._stage_buffer)
            except Exception:  # noqa: BLE001 — widget may not exist yet
                pass

    def _set_status(self, text: str) -> None:
        try:
            self.query_one(StatusBar).set_status(text)
        except Exception:  # noqa: BLE001 — widget may not exist yet
            pass


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = ProductResearchApp()
    app.run()
