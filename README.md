# 🔭 Prode — Research before you build

A terminal TUI that runs a full **8-stage product research pipeline** against any idea — powered by Claude (Anthropic) or a local/cloud Ollama model — and streams the results live in your terminal.

```
┌─────────────────────────────────────────────────────────┐
│  🔭  Prode  — Research before you build  v1.0.0 · Anthropic │
├─────────────────────────────────────────────────────────┤
│  Idea: [AI-powered code review tool for solo devs     ] │
│                              [  Run Research ▶  ]       │
├──────────────────┬──────────────────────────────────────┤
│  STAGES          │  ## Market Overview                  │
│                  │                                      │
│  ✓ Market        │  The AI code review market sits      │
│  ✓ Compete       │  within the broader $12B DevTools    │
│  ✓ Pain Pts      │  category...                         │
│  ⠸ ICP           │                                      │
│  ○ Sizing        │  | Competitor | Price | Strengths |  │
│  ○ Features      │  |------------|-------|------------|  │
│  ○ Position      │  | GitHub CoPi| $10/mo| IDE integr.|  │
│  ○ Verdict       │  | Cursor     | $20/mo| Fast UX    |  │
├──────────────────┴──────────────────────────────────────┤
│  [████████████░░░░░░░░] 3/8  Analyzing ICP…             │
│  [E]xport  [Q]uit  [R]eset  [Tab] focus  [↑↓] scroll   │
└─────────────────────────────────────────────────────────┘
```

---

## Features

- **8 research stages** — sequential, each a separate API call with its own focused prompt
- **Live streaming output** — tokens appear as they are generated
- **Web search** (Anthropic only) — model searches the web mid-response to ground findings in real data
- **Multi-provider** — Anthropic API, local Ollama, or any custom OpenAI-compatible endpoint
- **Provider setup modal** — choose your backend on startup; Anthropic key pre-filled from `.env`
- **Animated sidebar** — Braille spinner on the active stage, ✓/✗ on completion
- **Markdown rendering** — tables, headers, bold, code all render in the terminal
- **Keyboard-driven** — full shortcut set, no mouse required
- **One-command export** — press `E` to write a single `.md` file with all 8 sections

---

## Research Stages

| # | Stage | What it covers |
|---|-------|----------------|
| 1 | **Market Overview** | Problem space, market maturity, existing category, key trends, regulatory landscape |
| 2 | **Competitor Analysis** | 5–8 competitors in a table: pricing, strengths, weaknesses, funding |
| 3 | **Customer Pain Points** | Top frustrations with current solutions, emotional & economic pain, unmet needs |
| 4 | **ICP Definition** | 2–3 ideal customer profiles with role, goals, trigger events, WTP |
| 5 | **Market Sizing** | TAM / SAM / SOM via bottom-up and top-down methodology |
| 6 | **Feature Prioritization** | MoSCoW table (15–20 features), MVP scope, hardest technical challenge |
| 7 | **Positioning Angles** | 3 differentiation strategies, hero copy, recommended angle |
| 8 | **Verdict** | Go/No-Go score (1–10), scoring table, bull/bear case, critical assumptions, next steps |

---

## Prerequisites

- Python **3.11+**
- One of:
  - An [Anthropic API key](https://console.anthropic.com/) (for Claude + web search)
  - [Ollama](https://ollama.com/) running locally (`ollama serve`)
  - Any OpenAI-compatible endpoint (self-hosted or cloud)

---

## Installation

```bash
# 1. Clone / enter the project directory
cd product_researcher

# 2. Create a virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Set your Anthropic key so the modal pre-fills it
cp .env.example .env
# Edit .env and replace the placeholder with your real key
```

---

## Usage

```bash
python main.py
```

A setup modal appears on every launch so you can choose your provider.

### Provider Options

#### Anthropic (Claude + Web Search)
- Select **Anthropic** in the modal
- Enter your `ANTHROPIC_API_KEY`  
- Model: `claude-sonnet-4-6`  
- Web search is enabled automatically — the model searches the web mid-response

#### Ollama Local
- Start Ollama first: `ollama serve` and `ollama pull llama3.2`
- Select **Ollama Local** in the modal
- Enter the model name (e.g. `llama3.2`, `mistral`, `qwen2.5`)
- Optionally change the port if you run on a non-default port

#### Ollama Cloud / Custom Endpoint
- Select **Ollama Cloud / Custom Endpoint** in the modal
- Enter the full base URL of your endpoint (e.g. `https://my-ollama.example.com`)
- Enter the model name
- Optionally enter an API key if your endpoint requires one

> **Note:** Web search is only available with the Anthropic provider. Ollama and custom endpoints use the model's training knowledge only.

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Enter` | Submit idea / start research |
| `E` | Export all results to `./research_<slug>_<timestamp>.md` |
| `R` | Reset — clear everything and start over |
| `Q` / `Ctrl+Q` | Quit |
| `Tab` | Toggle focus between the idea input and the output panel |
| `↑` / `↓` | Scroll the output panel |

---

## Export Format

Pressing `E` writes a file to the current directory:

```
research_ai-powered-code-review_20260409_143022.md
```

Structure:
```markdown
# AI Product Research: <your idea>

*Generated on April 09, 2026 at 14:30:22*

---

## Market Overview

<stage content>

---

## Competitor Analysis

<stage content>

---
... (all 8 sections)
```

---

## Project Structure

```
product_researcher/
├── main.py          # Textual app — layout, widgets, keybindings, worker
├── researcher.py    # Provider-agnostic streaming: Anthropic + Ollama backends
├── stages.py        # Stage definitions (name, short_name, prompt_template)
├── exporter.py      # Markdown export logic
├── requirements.txt
├── .env.example     # ANTHROPIC_API_KEY=
└── README.md
```

### Key files

**`researcher.py`** — contains `ProviderConfig` (dataclass with `provider`, `model`, `api_key`, `base_url`) and two streaming backends:
- `_stream_anthropic()` — Anthropic SDK, enables `web_search_20250305` tool, yields typed `(event_type, content)` tuples
- `_stream_ollama()` — `openai.AsyncOpenAI` pointed at a custom `base_url`; works with any OpenAI-compatible server

**`stages.py`** — list of 8 `Stage` dataclasses. Each has a `prompt_template` with a `{idea}` placeholder that gets filled at runtime.

**`main.py`** — Textual `App` with:
- `ProviderSetupModal` — 3-option `RadioSet` that shows/hides the relevant form section
- `StagesSidebar` — custom `Widget` with reactive Braille spinner
- `StatusBar` — `ProgressBar` + live status label + shortcut hints
- `@work` async coroutine that drives the stage loop and handles rate-limit retries

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Only for Anthropic provider | Pre-fills the key field in the setup modal |

Copy `.env.example` to `.env` and fill it in:

```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

---

## Supported Models

### Anthropic
| Model | Notes |
|-------|-------|
| `claude-sonnet-4-6` | Default — best balance of quality and speed |
| `claude-opus-4-6` | Highest quality, slower |
| `claude-haiku-4-5-20251001` | Fastest, lower cost |

### Ollama (examples)
| Model | Pull command |
|-------|-------------|
| `llama3.2` | `ollama pull llama3.2` |
| `mistral` | `ollama pull mistral` |
| `qwen2.5` | `ollama pull qwen2.5` |
| `deepseek-r1` | `ollama pull deepseek-r1` |
| `phi4` | `ollama pull phi4` |

Any model available in your Ollama instance or at your custom endpoint will work.

---

## Error Handling

| Situation | Behaviour |
|-----------|-----------|
| Rate limit | 5-second countdown shown in status bar, then automatic retry |
| Network error | Error message appended inline in the output panel; stage marked ✗; pipeline continues |
| Stage failure | Stage marked ✗ in sidebar; partial text saved; next stage starts |
| Missing API key | Submit button does nothing until the field is filled |
| Ollama not running | Connection error shown inline; remaining stages continue |

---

## License

MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
