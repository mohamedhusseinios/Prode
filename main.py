#!/usr/bin/env python3
"""
AI Product Research Tool
Terminal TUI powered by Textual + Anthropic/Ollama + Web Search
"""

import asyncio
import os
import time
from typing import Dict, Optional

from dotenv import load_dotenv
from rich.text import Text
from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Input,
    Label,
    Markdown,
    ProgressBar,
    RadioButton,
    RadioSet,
    TextArea,
)
from textual.widget import Widget

from config import load_config, save_config
from exporter import export_results
from researcher import ProviderConfig, stream_stage
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
                "[E]xport  [C]onfigure  [Q]uit  [Tab] focus  [↑↓] scroll",
                id="hints",
                markup=False,
            )

    def set_status(self, text: str) -> None:
        try:
            self.query_one("#stage-label", Label).update(text)
        except Exception:
            pass

    def set_progress(self, done: int) -> None:
        try:
            self.query_one("#bar", ProgressBar).progress = done
        except Exception:
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
        Binding("tab", "toggle_focus", "Toggle focus"),
        Binding("ctrl+enter", "run_research", "Run", show=False, priority=True),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._config: Optional[ProviderConfig] = None
        self._results: Dict[str, str] = {}
        self._current_idea: str = ""
        self._running: bool = False
        self._output_buffer: str = ""   # full accumulated text (for export)
        self._stage_buffer: str = ""    # current stage only (for live display)
        self._pending_refresh: bool = False
        self._last_flush_time: float = 0.0

    # ── Layout ────────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        with Container(id="app-header"):
            yield Label("🔭  Prode  — Research before you build", id="header-title")
            yield Label(VERSION, id="header-provider")

        with Container(id="input-section"):
            yield Label("💡", id="idea-label")
            yield IdeaInput()
            yield Button("▶ Research", variant="primary", id="run-btn")

        with Horizontal(id="main-area"):
            yield StagesSidebar()
            with Container(id="output-scroll"):
                yield Markdown("", id="output-md")

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
        self.action_run_research()

    # ── Actions ───────────────────────────────────────────────────────────────

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
        self._current_idea = idea
        self._results = {}
        self._running = True
        self.query_one(StagesSidebar).reset()
        self.query_one(StatusBar).reset()
        self._output_buffer = f"# Product Research: {idea}\n\n"
        self._stage_buffer = f"# Product Research: {idea}\n\n"
        self._pending_refresh = False
        try:
            self.query_one("#output-md", Markdown).update(self._stage_buffer)
        except Exception:
            pass
        self.notify(f"Starting research for: {idea[:50]}", timeout=3)
        self._run_all_stages()

    def action_export(self) -> None:
        if not self._results:
            self._set_status("⚠  Nothing to export yet.")
            return
        try:
            path = export_results(self._current_idea, self._results)
            self._set_status(f"✓  Saved to {path}")
        except Exception as exc:
            self._set_status(f"✗  Export failed: {exc}")

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

    def action_toggle_focus(self) -> None:
        inp = self.query_one("#idea-input", IdeaInput)
        scroll = self.query_one("#output-scroll")
        if inp.has_focus:
            scroll.focus()
        else:
            inp.focus()

    def action_quit(self) -> None:
        self.exit()

    # ── Research worker ───────────────────────────────────────────────────────

    @work(name="research")
    async def _run_all_stages(self) -> None:
        """Sequentially stream all 8 research stages."""
        try:
            sidebar = self.query_one(StagesSidebar)
            status_bar = self.query_one(StatusBar)
            for idx, stage in enumerate(STAGES):
                sidebar.set_status(stage.id, "running")
                status_bar.set_status(f"⟳  {stage.name}…")
                status_bar.set_progress(idx)

                self._output_buffer += f"\n\n## {stage.name}\n\n"
                self._stage_buffer = f"## {stage.name}\n\n"
                try:
                    self.query_one("#output-md", Markdown).update(self._stage_buffer)
                except Exception:
                    pass

                prompt = stage.prompt_template.format(idea=self._current_idea)
                stage_text = ""
                success = True
                last_etype = ""

                while True:
                    async for etype, content in stream_stage(self._config, prompt):
                        last_etype = etype

                        if etype == "text":
                            stage_text += content
                            self._append_output(content)

                        elif etype == "searching":
                            status_bar.set_status("🌐  Searching the web…")

                        elif etype == "search_done":
                            status_bar.set_status(f"⟳  {stage.name}…")

                        elif etype == "rate_limit":
                            for secs in range(RATE_LIMIT_WAIT, 0, -1):
                                status_bar.set_status(
                                    f"⏳  Rate limited — retrying in {secs}s…"
                                )
                                await asyncio.sleep(1)
                            break  # retry

                        elif etype == "error":
                            self._append_output(
                                f"\n\n> ⚠ **Error during {stage.name}:** {content}\n\n"
                            )
                            self.notify(
                                f"Error — {stage.name}: {content[:120]}",
                                severity="error",
                                timeout=10,
                            )
                            success = False
                            break

                    else:
                        break  # for-loop completed normally → done

                    if last_etype == "error":
                        break  # don't retry on hard errors

                self._results[stage.id] = stage_text
                sidebar.set_status(stage.id, "done" if success else "failed")
                status_bar.set_progress(idx + 1)

            status_bar.set_status("✓  Research complete — press E to export")
            self.notify("Research complete! Press E to export.", timeout=5)

        except Exception as exc:
            self._append_output(f"\n\n> ✗ **Unexpected error:** {exc}\n\n")
            status_bar.set_status(f"✗  Error: {exc}")
            self.notify(f"Unexpected error: {exc}", severity="error", timeout=15)

        finally:
            self._running = False

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _update_output(self, content: str) -> None:
        self._output_buffer = content
        try:
            self.query_one("#output-md", Markdown).update(content)
        except Exception:
            pass

    def _append_output(self, chunk: str) -> None:
        self._output_buffer += chunk
        self._stage_buffer += chunk
        if not self._pending_refresh:
            self._pending_refresh = True
            elapsed = time.monotonic() - self._last_flush_time
            delay = max(0.0, 0.15 - elapsed)
            self.set_timer(delay, self._flush_output)

    def _flush_output(self) -> None:
        self._pending_refresh = False
        self._last_flush_time = time.monotonic()
        try:
            self.query_one("#output-md", Markdown).update(self._stage_buffer)
            self.query_one("#output-scroll").scroll_end(animate=False)
        except Exception:
            pass

    def _set_status(self, text: str) -> None:
        try:
            self.query_one(StatusBar).set_status(text)
        except Exception:
            pass


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = ProductResearchApp()
    app.run()
