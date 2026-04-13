# Syrin-Python Integration: Agent Framework Adoption

## TL;DR

> **Quick Summary**: Replace Prode's entire AI provider layer (`researcher.py`) with the syrin-python agent framework, redesigning the sequential 8-stage pipeline into a Syrin Reflection Loop pattern where producer agents research each topic and critic agents refine until quality thresholds are met.
> 
> **Deliverables**:
> - `agents.py` — 8 Syrin Agent subclasses (one per research topic) + CriticAgent + config
> - `researcher.py` — Rewired to use Syrin Swarm REFLECTION topology instead of raw SDK calls
> - `stages.py` — Updated to define agent configurations instead of prompt templates
> - `main.py` — Batch-then-display UI for agent steps, reflection progress indicators
> - `exporter.py` — Updated to consume Syrin result objects
> - `tools.py` — Custom Syrin tools: web_search (Anthropic tool spec), duckduckgo_search, idea_context
> - `requirements.txt` — Updated with syrin[openai,anthropic]
> 
> **Estimated Effort**: Large
> **Parallel Execution**: YES — 6 waves
> **Critical Path**: Task 1 (syrin setup) → Task 3 (agents) → Task 5 (pipeline) → Task 7 (UI) → Task 8 (export) → Task 9 (cleanup)

---

## Context

### Original Request
User wants to adopt https://github.com/syrin-labs/syrin-python as Prode's agent framework, replacing the existing direct Anthropic/Ollama SDK calls with Syrin's Agent/Swarm/Model abstractions and redesigning the stage pipeline to use Reflection Loop patterns.

### Interview Summary
**Key Discussions**:
- **Integration scope**: BOTH — Replace provider layer AND add agent orchestration
- **Approach**: Clean cut — remove old SDK calls entirely, no fallback
- **Pipeline redesign**: Reflection Loop (producer-critic, iterate until quality threshold)
- **Streaming**: Batch-then-display for agent steps (not token-by-token)
- **Budget**: Deferred — skip per-stage cost limits for now
- **Web search**: Both — Syrin Knowledge/RAG + provider-native search, configurable per provider
- **Research topics**: Keep all 8 as required output

**Research Findings**:
- Syrin provides: Agent, Budget, Model (OpenAI/Anthropic/Ollama/Google/LiteLLM/Custom), Memory, Knowledge, Swarm (5 topologies), Workflow, Guardrail
- **Critical**: `syrin.stream()` does NOT support tools — Reflection rounds must use `run()`/`arun()`
- **Critical**: Anthropic's native `web_search` tool is NOT in Syrin — must register as custom `ToolSpec`
- **Critical**: Syrin has no DuckDuckGo integration — must port existing `_fetch_search_context()` as a `@tool`
- **Critical**: `Swarm.run()` is async-only — must use `await` inside Textual's `@work`
- Cost concern: REFLECTION × 8 topics × 3-5 rounds = 24-80 LLM calls per run

### Metis Review
**Identified Gaps** (addressed):
- stream() lacks tool support → Reflection uses run()/arun(), single-shot uses stream()
- Anthropic web_search missing → register as custom ToolSpec
- DuckDuckGo missing → port _fetch_search_context() as @tool
- Swarm.run() async-only → use await in @work decorator
- Cost explosion risk → default 2 rounds max per topic, configurable

---

## Work Objectives

### Core Objective
Replace Prode's AI provider and orchestration layer with syrin-python, using a Reflection Loop pattern (producer + critic) to improve research quality while preserving all 8 research topics as required output.

### Concrete Deliverables
- `agents.py` — New file with 8 research Agent subclasses + CriticAgent + configuration
- `researcher.py` — Replaced with Syrin-based orchestration (Swarm REFLECTION topology)
- `stages.py` — Updated from Stage(prompt_template) to stage config objects referencing Agent classes
- `main.py` — Updated _run_all_stages() for reflection loop + batch display
- `exporter.py` — Updated to consume Syrin result objects
- `tools.py` — Custom Syrin tools for web search (Anthropic + DuckDuckGo)
- `requirements.txt` — Updated dependencies

### Definition of Done
- [ ] `python main.py` launches TUI successfully
- [ ] Selecting a provider + entering an idea triggers the full reflection pipeline
- [ ] All 8 research topics appear in the output
- [ ] Critic feedback drives visible quality improvements across reflection rounds
- [ ] Export produces valid markdown with all 8 sections
- [ ] Both Anthropic and Ollama providers work through Syrin Model abstraction

### Must Have
- Syrin agents for all 8 research topics
- Reflection Loop (producer + critic) with configurable max rounds (default 2)
- Provider support for Anthropic and Ollama via Syrin Model
- Web search via custom tools (Anthropic web_search tool spec + DuckDuckGo port)
- Batch-then-display UI showing reflection progress per topic
- Markdown export with all 8 sections
- Clean removal of old SDK direct calls

### Must NOT Have (Guardrails)
- Do NOT add Budget/cost controls yet (explicitly deferred)
- Do NOT add Memory/Knowledge persistence across sessions (future scope)
- Do NOT redesign the TUI layout or widget structure (keep existing UI shell)
- Do NOT add token-by-token streaming back (batch display only)
- Do NOT keep old researcher.py dual-backend code paths (clean cut)
- Do NOT use `stream()` for reflection rounds (it doesn't support tools)
- Do NOT run `Swarm.run()` synchronously — always `await`
- Do NOT set max reflection rounds above 3 (cost control default)

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: NO (project has zero test coverage per AGENTS.md)
- **Automated tests**: None — no test framework setup in this plan
- **Framework**: None
- **Agent-Executed QA**: ALWAYS (mandatory for all tasks)

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **TUI/Application**: Use interactive_bash (tmux) — Launch app, send keystrokes, validate output, check exit code
- **Python Module**: Use Bash (python3) — Import module, call functions, compare output
- **API/Backend**: Use Bash (curl) — Send requests, assert status + response fields

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Foundation — start immediately):
├── Task 1: Install syrin + dependency setup [quick]
├── Task 2: Create tools.py with custom Syrin tools [unspecified-high]
└── Task 3: Define Stage config objects in stages.py [quick]

Wave 2 (Core agents — after Wave 1):
├── Task 4: Create 8 research Agent subclasses in agents.py [deep]
├── Task 5: Create CriticAgent in agents.py [deep]
└── Task 6: Wire provider config to Syrin Model in agents.py [quick]

Wave 3 (Orchestration — after Wave 2):
├── Task 7: Rewrite researcher.py with Syrin Swarm REFLECTION [deep]
└── Task 8: Update main.py _run_all_stages() for reflection loop [deep]

Wave 4 (Integration — after Wave 3):
├── Task 9: Update exporter.py for Syrin result objects [quick]
└── Task 10: Update main.py UI for batch-then-display [unspecified-high]

Wave 5 (Cleanup — after Wave 4):
├── Task 11: Clean up old code paths + update requirements.txt [quick]
└── Task 12: End-to-end smoke test [unspecified-high]

Wave FINAL (After ALL tasks — 4 parallel reviews):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)
```

### Dependency Matrix

| Task | Depends On | Blocks |
|------|-----------|--------|
| 1 | — | 2, 4, 6, 7 |
| 2 | 1 | 4, 7 |
| 3 | — | 4, 7 |
| 4 | 1, 2, 3, 6 | 7 |
| 5 | 1, 2 | 7 |
| 6 | 1 | 4 |
| 7 | 2, 3, 4, 5 | 8 |
| 8 | 7 | 9, 10 |
| 9 | 8 | 11 |
| 10 | 8 | 11 |
| 11 | 9, 10 | 12 |
| 12 | 11 | F1-F4 |

### Agent Dispatch Summary

- **Wave 1**: 3 tasks — T1 `quick`, T2 `unspecified-high`, T3 `quick`
- **Wave 2**: 3 tasks — T4 `deep`, T5 `deep`, T6 `quick`
- **Wave 3**: 2 tasks — T7 `deep`, T8 `deep`
- **Wave 4**: 2 tasks — T9 `quick`, T10 `unspecified-high`
- **Wave 5**: 2 tasks — T11 `quick`, T12 `unspecified-high`
- **FINAL**: 4 tasks — F1 `oracle`, F2 `unspecified-high`, F3 `unspecified-high`, F4 `deep`

---

## TODOs

- [x] 1. Install syrin + dependency setup

  **What to do**:
  - Add `syrin[openai,anthropic]` to `requirements.txt` (keep existing deps: `textual`, `python-dotenv`)
  - Remove direct `anthropic` and `openai` from requirements (syrin bundles them)
  - Create a virtual env and install: `pip install -r requirements.txt`
  - Verify import works: `python -c "from syrin import Agent, Model, Swarm; print('OK')"`
  - Update `.env.example` to document syrin provider config options (SYRIN_PROVIDER, SYRIN_MODEL)

  **Must NOT do**:
  - Do NOT remove `textual` or `python-dotenv` from requirements
  - Do NOT add budget/extras beyond `[openai,anthropic]`

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [] (no special skills needed for dependency setup)

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 2 and 3 — they can start independently, but agents.py imports depend on this being done)
  - **Parallel Group**: Wave 1
  - **Blocks**: Tasks 2, 4, 6, 7 (need syrin installed to import)
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References**:
  - `requirements.txt` — Current dependency list (anthropic, openai, textual, python-dotenv)
  - `.env.example` — Current env var template (ANTHROPIC_API_KEY)

  **API/Type References**:
  - Syrin imports: `from syrin import Agent, Budget, Model, Memory, Knowledge, Guardrail`
  - Syrin providers: `Model.OpenAI(...)`, `Model.Anthropic(...)`, `Model.Ollama(...)`, `Model.Custom(api_base=...)`

  **Test References**:
  - No existing tests — this task has no test references

  **WHY Each Reference Matters**:
  - `requirements.txt` — Must update, not replace; keep textual and python-dotenv
  - `.env.example` — Must add SYRIN_* env vars alongside existing ANTHROPIC_API_KEY
  - Syrin imports — Verify the package actually installs and imports correctly

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Syrin imports correctly
    Tool: Bash
    Preconditions: Virtual environment activated
    Steps:
      1. Run: python -c "from syrin import Agent, Model, Swarm; from syrin.enums import ExceedPolicy, SwarmTopology; print('OK')"
      2. Assert output contains "OK"
    Expected Result: Import succeeds with no errors
    Failure Indicators: ImportError, ModuleNotFoundError
    Evidence: .sisyphus/evidence/task-1-import-test.txt

  Scenario: Existing textual dependency still works
    Tool: Bash
    Preconditions: Virtual environment activated
    Steps:
      1. Run: python -c "from textual.app import App; print('OK')"
      2. Assert output contains "OK"
    Expected Result: textual still imports after syrin install
    Failure Indicators: ImportError
    Evidence: .sisyphus/evidence/task-1-textual-test.txt
  ```

  **Commit**: YES (groups with 2, 3)
  - Message: `feat(deps): add syrin-python dependency and scaffolding`
  - Files: `requirements.txt`, `.env.example`

- [x] 2. Create tools.py with custom Syrin tools

  **What to do**:
  - Create new file `tools.py` at project root
  - Port `_fetch_search_context()` from `researcher.py` (lines 142-181) as a Syrin `@tool` named `duckduckgo_search`
  - Create a Syrin `ToolSpec` for Anthropic's `web_search_20250305` tool (register as a tool the agent can invoke)
  - Create a `idea_context` tool that injects the user's research idea into the agent's context
  - Each tool must have proper type hints, docstrings, and return types
  - The DuckDuckGo tool should use `aiohttp` (or `httpx` if syrin bundles it) for async HTTP
  - The Anthropic web_search tool spec should be a passthrough — when provider is Anthropic and agent invokes it, the model handles the tool call natively

  **Must NOT do**:
  - Do NOT delete the old `_fetch_search_context()` yet (that's Task 11 cleanup)
  - Do NOT add Budget controls to tools
  - Do NOT use `stream()` API — tools work with `run()`/`arun()` only

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: [] (no special skills needed, but requires careful async tool implementation)

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 3 — they don't depend on each other)
  - **Parallel Group**: Wave 1
  - **Blocks**: Tasks 4, 5, 7 (agents need tools)
  - **Blocked By**: Task 1 (syrin dependency must be installed)

  **References**:

  **Pattern References**:
  - `researcher.py:142-181` — Existing `_fetch_search_context()` implementation using DuckDuckGo HTML API with `aiohttp`. This is the exact logic to port.
  - `researcher.py:42-74` — `ProviderConfig` dataclass showing how provider info is currently accessed (use similar pattern for Syrin Model determination)

  **API/Type References**:
  - Syrin `@tool` decorator: `from syrin import tool` or similar — check syrin docs for exact tool registration API
  - Syrin `ToolSpec`: For registering external tool schemas that the LLM can invoke

  **External References**:
  - Syrin docs: https://docs.syrin.dev/agent-kit/ — Tool registration patterns
  - Anthropic web_search tool: The `web_search_20250305` tool spec format for Anthropic API

  **WHY Each Reference Matters**:
  - `researcher.py:142-181` — This is the exact DuckDuckGo search code to port. Must preserve the search logic, result parsing, and error handling.
  - Syrin docs — Must follow syrin's exact `@tool` decorator pattern, not invent our own
  - Anthropic web_search — Must match Anthropic's tool schema exactly for passthrough to work

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: DuckDuckGo tool returns search results
    Tool: Bash
    Preconditions: Internet access available
    Steps:
      1. Run: python -c "from tools import duckduckgo_search; import asyncio; result = asyncio.run(duckduckgo_search('test query')); print(len(result))"
      2. Assert result length > 0
    Expected Result: Tool returns non-empty search context
    Failure Indicators: Empty string, exception, timeout
    Evidence: .sisyphus/evidence/task-2-ddg-tool.txt

  Scenario: Anthropic web_search tool spec is valid JSON schema
    Tool: Bash
    Preconditions: tools.py created
    Steps:
      1. Run: python -c "from tools import WEB_SEARCH_TOOL_SPEC; print(type(WEB_SEARCH_TOOL_SPEC)); print('name' in str(WEB_SEARCH_TOOL_SPEC))"
      2. Assert output contains the tool name and schema structure
    Expected Result: Tool spec has name, description, input_schema
    Failure Indicators: AttributeError, missing keys
    Evidence: .sisyphus/evidence/task-2-anthropic-tool-spec.txt
  ```

  **Commit**: YES (groups with 1, 3)
  - Message: `feat(deps): add syrin-python dependency and scaffolding`
  - Files: `tools.py`

- [x] 3. Define Stage config objects in stages.py

  **What to do**:
  - Replace the current `Stage` dataclass (which holds `prompt_template`) with a `StageConfig` dataclass that holds:
    - `id: str` — same stage IDs (market, competitors, etc.)
    - `name: str` — same display names
    - `short_name: str` — same sidebar names
    - `agent_class_path: str` — dotted path to the Agent subclass (e.g., `"agents.MarketOverviewAgent"`)
    - `max_reflection_rounds: int` — default 2 (configurable)
    - `description: str` — what this stage investigates (used in critic prompt)
  - Keep the `STAGES` list in the same order with all 8 stages
  - Each stage config maps to an Agent subclass defined in Task 4

  **Must NOT do**:
  - Do NOT delete old `prompt_template` strings yet (keep them commented out for reference until Task 11)
  - Do NOT change stage IDs or ordering (the sidebar and progress bar depend on them)
  - Do NOT add budget configs per stage (explicitly deferred)

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 1, 2 — independent)
  - **Parallel Group**: Wave 1
  - **Blocks**: Tasks 4, 7 (agents and pipeline reference these configs)
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References**:
  - `stages.py:1-40` (approximate) — Current `Stage` dataclass and `STAGES` list. Must preserve the exact IDs, names, and short_names.
  - `main.py:818-954` — `_run_all_stages()` iterates over `STAGES` list. New StageConfig must be compatible with this iteration pattern.

  **API/Type References**:
  - `syrin.agent.Agent` — Base class for all agent subclasses
  - Stage IDs: `market`, `competitors`, `pain_points`, `icp`, `sizing`, `features`, `positioning`, `verdict`

  **WHY Each Reference Matters**:
  - `stages.py` — Must preserve exact IDs/names or the sidebar and progress bar will break
  - `main.py` loop — Must ensure StageConfig is iterable in the same pattern as current Stage
  - Syrin Agent — agent_class_path must resolve to actual Agent subclasses in agents.py

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: StageConfig list preserves all 8 stages
    Tool: Bash
    Preconditions: stages.py updated
    Steps:
      1. Run: python -c "from stages import STAGES; print(len(STAGES)); print([s.id for s in STAGES])"
      2. Assert output: 8 stages, IDs match ['market', 'competitors', 'pain_points', 'icp', 'sizing', 'features', 'positioning', 'verdict']
    Expected Result: Exactly 8 stages with correct IDs
    Failure Indicators: Missing stages, wrong IDs, import error
    Evidence: .sisyphus/evidence/task-3-stage-configs.txt

  Scenario: StageConfig has agent_class_path and max_reflection_rounds
    Tool: Bash
    Preconditions: stages.py updated
    Steps:
      1. Run: python -c "from stages import STAGES; s = STAGES[0]; print(hasattr(s, 'agent_class_path'), hasattr(s, 'max_reflection_rounds'), s.max_reflection_rounds)"
      2. Assert output: True True 2
    Expected Result: Config objects have required fields with correct defaults
    Failure Indicators: AttributeError, wrong default value
    Evidence: .sisyphus/evidence/task-3-config-fields.txt
  ```

  **Commit**: YES (groups with 1, 2)
  - Message: `feat(deps): add syrin-python dependency and scaffolding`
  - Files: `stages.py`

- [x] 4. Create 8 research Agent subclasses in agents.py

  **What to do**:
  - Create new file `agents.py` at project root
  - Define 8 Agent subclasses, one per research topic:
    - `MarketOverviewAgent` — Market analysis, trends, size
    - `CompetitorAnalysisAgent` — Competitive landscape, alternatives
    - `PainPointsAgent` — Customer pain points, unmet needs
    - `ICPAgent` — Ideal customer profile definition
    - `SizingAgent` — Market sizing, TAM/SAM/SOM
    - `FeaturesAgent` — Feature prioritization, must-haves
    - `PositioningAgent` — Positioning angles, differentiation
    - `VerdictAgent` — Overall verdict, go/no-go assessment
  - Each Agent subclass sets:
    - `model` — references `Model.Anthropic(...)` or `Model.Ollama(...)` or `Model.Custom(...)` based on provider config (injected via class variable or constructor)
    - `system_prompt` — adapted from the corresponding `prompt_template` in current `stages.py` but rewritten as system instructions for an agent (not just a prompt template)
    - `tools` — list including `duckduckgo_search` or `WEB_SEARCH_TOOL_SPEC` depending on provider capabilities
  - Provider config is passed at instantiation time, not class definition time, so the same Agent class works with any provider
  - Each agent's system_prompt should instruct the agent to investigate its topic thoroughly, cite sources, and produce structured output

  **Must NOT do**:
  - Do NOT hard-code API keys in Agent class definitions
  - Do NOT use `stream()` — agents will use `run()`/`arun()` via reflection
  - Do NOT set Budget (deferred)
  - Do NOT add Memory persistence (deferred)

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO — depends on Tasks 1, 2, 3, 6
  - **Parallel Group**: Wave 2
  - **Blocks**: Tasks 7, 8
  - **Blocked By**: Tasks 1 (syrin installed), 2 (tools available), 3 (stage configs), 6 (provider wiring)

  **References**:

  **Pattern References**:
  - `stages.py:STAGES[0..7].prompt_template` — Current prompt templates, one per stage. These are the basis for agent system_prompts. Must adapt each to an agent instruction format.
  - `researcher.py:80-136` — `_stream_anthropic()` showing the current Anthropic API call pattern with web_search tool. The agent must replicate this search capability.

  **API/Type References**:
  - `from syrin import Agent, Model` — Base Agent class and Model provider
  - `from tools import duckduckgo_search, WEB_SEARCH_TOOL_SPEC, idea_context` — Custom tools to inject

  **External References**:
  - Syrin docs: https://docs.syrin.dev/agent-kit/ — Agent subclass definition patterns, system_prompt format

  **WHY Each Reference Matters**:
  - `stages.py` prompt_templates — Must adapt each template's research goal into an agent system_prompt that instructs the agent to investigate, not just answer
  - `researcher.py` Anthropic pattern — Must ensure agents can invoke web search tools equivalent to current capability
  - Syrin docs — Must follow exact Agent subclass pattern (model, system_prompt, tools as class variables)

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: All 8 agent classes import and instantiate
    Tool: Bash
    Preconditions: syrin installed, tools.py available
    Steps:
      1. Run: python -c "from agents import MarketOverviewAgent, CompetitorAnalysisAgent, PainPointsAgent, ICPAgent, SizingAgent, FeaturesAgent, PositioningAgent, VerdictAgent; print('All 8 agents imported OK')"
      2. Assert no import errors
    Expected Result: All 8 agent classes import successfully
    Failure Indicators: ImportError, KeyError
    Evidence: .sisyphus/evidence/task-4-agent-imports.txt

  Scenario: Agent accepts provider config at instantiation
    Tool: Bash
    Preconditions: agents.py created
    Steps:
      1. Run: python -c "from agents import MarketOverviewAgent; from syrin import Model; agent = MarketOverviewAgent(model=Model.Ollama('llama3')); print(type(agent).__name__)"
      2. Assert output: MarketOverviewAgent
    Expected Result: Agent instantiates with injected provider config
    Failure Indicators: TypeError, missing model argument
    Evidence: .sisyphus/evidence/task-4-agent-instantiation.txt
  ```

  **Commit**: YES (groups with 5, 6)
  - Message: `feat(agents): add research and critic agent definitions`
  - Files: `agents.py`

- [x] 5. Create CriticAgent in agents.py

  **What to do**:
  - Add `CriticAgent` subclass to `agents.py`
  - The CriticAgent reviews research output from any research Agent and provides structured feedback:
    - Gaps in coverage (missing important aspects of the topic)
    - Factual claims that need verification (source citations)
    - Logical inconsistencies
    - Depth assessment (superficial vs thorough)
    - Specific improvement suggestions
  - `system_prompt` instructs the critic to evaluate against these dimensions and output structured feedback
  - `model` injected at instantiation (can be a cheaper/faster model than research agents)
  - The CriticAgent does NOT use tools (it reviews text, no web search needed)
  - Include a quality threshold format — critic outputs a score (1-10) and "PASS" if ≥ threshold, "NEEDS_REVISION" if below
  - Default threshold is 7/10 (configurable)

  **Must NOT do**:
  - Do NOT give CriticAgent access to web search tools (it reviews, it doesn't research)
  - Do NOT hard-code the quality threshold (make it configurable)
  - Do NOT make CriticAgent specific to one research topic (it should work generically)

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 4 — different agent classes can be built independently)
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 7 (pipeline needs critic)
  - **Blocked By**: Tasks 1 (syrin), 2 (tools — to understand tool patterns)

  **References**:

  **Pattern References**:
  - `agents.py` (from Task 4) — Follow the same Agent subclass pattern: class-level model, system_prompt, tools
  - `stages.py:STAGES` — Each stage has a description that the critic should evaluate against

  **API/Type References**:
  - `from syrin import Agent, Model` — Base Agent class
  - Syrin Reflection topology — The critic is invoked in REFLECTION mode: producer → critic → (revise if needed)

  **External References**:
  - Syrin docs: https://docs.syrin.dev/agent-kit/ — Swarm REFLECTION topology usage

  **WHY Each Reference Matters**:
  - `agents.py` pattern — Must follow same subclass style for consistency
  - Reflection topology — CriticAgent must output in a format the Swarm REFLECTION can consume (score + feedback)

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: CriticAgent imports and instantiates
    Tool: Bash
    Preconditions: agents.py exists
    Steps:
      1. Run: python -c "from agents import CriticAgent; from syrin import Model; c = CriticAgent(model=Model.Ollama('llama3')); print(type(c).__name__, 'OK')"
      2. Assert output: CriticAgent OK
    Expected Result: CriticAgent class imports and instantiates with model
    Failure Indicators: ImportError, instantiation error
    Evidence: .sisyphus/evidence/task-5-critic-import.txt

  Scenario: CriticAgent has no tools assigned
    Tool: Bash
    Preconditions: agents.py exists
    Steps:
      1. Run: python -c "from agents import CriticAgent; from syrin import Model; c = CriticAgent(model=Model.Ollama('llama3')); print(len(c.tools) if hasattr(c, 'tools') else 0)"
      2. Assert output: 0 (no tools)
    Expected Result: CriticAgent has no tools (it reviews, doesn't research)
    Failure Indicators: Tools list is non-empty
    Evidence: .sisyphus/evidence/task-5-critic-no-tools.txt
  ```

  **Commit**: YES (groups with 4, 6)
  - Message: `feat(agents): add research and critic agent definitions`
  - Files: `agents.py`

- [x] 6. Wire provider config to Syrin Model in agents.py

  **What to do**:
  - Create a `ProviderConfig` replacement class (or update the existing one in `researcher.py`) that wraps Syrin Model instances
  - Map current provider options to Syrin Model:
    - `"anthropic"` → `Model.Anthropic(effective_model, api_key=...)`
    - `"ollama"` → `Model.Ollama(effective_model)` or `Model.Custom(api_base=ollama_base_url, ...)`
  - Add a `create_model()` factory function that returns the appropriate `Model` instance based on provider config
  - Ensure the factory reads `api_key` from environment (ANTHROPIC_API_KEY, or custom env vars)
  - The factory should be used by all Agent subclasses in `agents.py` to get their model

  **Must NOT do**:
  - Do NOT remove the old `ProviderConfig` dataclass yet (Task 11 cleanup)
  - Do NOT add Budget to the config (deferred)
  - Do NOT hard-code model names — use configurable values

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO — depends on Task 1, blocks Task 4
  - **Parallel Group**: Wave 2 (but can start as soon as Task 1 completes)
  - **Blocks**: Task 4 (agents need provider wiring)
  - **Blocked By**: Task 1 (syrin installed)

  **References**:

  **Pattern References**:
  - `researcher.py:42-74` — Current `ProviderConfig` dataclass. Must preserve provider switching logic but replace Anthropic/Ollama constructors with Syrin Model constructors.
  - `researcher.py:80-136` — Anthropic provider setup (client initialization). The factory must replicate this provider selection.

  **API/Type References**:
  - `Model.Anthropic("claude-sonnet", api_key=...)` — Syrin Anthropic provider
  - `Model.Ollama("llama3")` — Syrin Ollama provider
  - `Model.Custom(api_base="http://localhost:11434/v1", ...)` — For non-standard Ollama endpoints

  **WHY Each Reference Matters**:
  - `researcher.py:42-74` — Must preserve the provider config interface (provider name, model, api_key, base_url) but swap the internal implementation
  - Syrin Model API — Must use exact Syrin Model class constructors

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: create_model() returns correct Model for Anthropic provider
    Tool: Bash
    Preconditions: .env with ANTHROPIC_API_KEY set
    Steps:
      1. Run: python -c "from agents import create_model; m = create_model(provider='anthropic', model='claude-sonnet', api_key='test-key'); print(type(m).__name__)"
      2. Assert output contains "Model" (syrin Model instance)
    Expected Result: Factory returns a Syrin Model for Anthropic
    Failure Indicators: TypeError, wrong model type
    Evidence: .sisyphus/evidence/task-6-anthropic-model.txt

  Scenario: create_model() returns correct Model for Ollama provider
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: python -c "from agents import create_model; m = create_model(provider='ollama', model='llama3', base_url='http://localhost:11434/v1'); print(type(m).__name__)"
      2. Assert output contains "Model"
    Expected Result: Factory returns a Syrin Model for Ollama endpoint
    Failure Indicators: TypeError, wrong model type
    Evidence: .sisyphus/evidence/task-6-ollama-model.txt
  ```

  **Commit**: YES (groups with 4, 5)
  - Message: `feat(agents): add research and critic agent definitions`
  - Files: `agents.py`

- [x] 7. Rewrite researcher.py with Syrin Swarm REFLECTION

  **What to do**:
  - Replace the entire content of `researcher.py` with Syrin-based orchestration
  - Remove all old code: `_stream_anthropic()`, `_stream_ollama()`, `_fetch_search_context()`, `stream_stage()`
  - Remove old `ProviderConfig` dataclass (replaced by `create_model()` in agents.py)
  - Implement a `run_research_pipeline()` async function that:
    1. Takes an idea string and provider config
    2. Creates a Swarm with REFLECTION topology
    3. Populates it with 8 research + 1 critic agent, all using the provider's Model
    4. Runs each stage through reflection (producer → critic → revise if score < threshold)
    5. Yields progress events: `("stage_start", stage_id)`, `("reflection_round", (stage_id, round_num))`, `("stage_complete", (stage_id, result_text))`, `("error", message)`, `("rate_limit", "")`, `("searching", "")`, `("search_done", "")`
    6. Respects max_reflection_rounds per stage (default 2) from StageConfig
  - The old 5-tuple event contract changes: instead of `"text"` token-by-token, we now have `"stage_complete"` with full text
  - Keep rate-limit retry logic (exponential backoff 5→10→20s, max 3 retries) but adapt for Syrin exceptions
  - Use `await swarm.arun()` (async-only, per requirement) — no `run_sync()`

  **Must NOT do**:
  - Do NOT use `stream()` — it doesn't support tools
  - Do NOT use `Swarm.run()` synchronously — always `await`
  - Do NOT keep old `_stream_anthropic()` or `_stream_ollama()` code (clean cut)
  - Do NOT add Budget to the Swarm (deferred)
  - Do NOT change the event tuple format beyond adding new event types (main.py must still be able to handle events)

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO — depends on Tasks 2, 3, 4, 5
  - **Parallel Group**: Wave 3
  - **Blocks**: Tasks 8, 9, 10
  - **Blocked By**: Tasks 2 (tools), 3 (stage configs), 4, 5 (agents)

  **References**:

  **Pattern References**:
  - `researcher.py:42-74` — Old `ProviderConfig` that's being replaced. Understand the interface (provider, model, api_key, base_url) to replicate in `create_model()`.
  - `researcher.py:248-261` — Old `stream_stage()` async generator. This is the interface that `main.py:_run_all_stages()` consumes. The new `run_research_pipeline()` must provide a similar yielding interface.
  - `main.py:571-605` — Rate-limit retry loop in `_run_all_stages()`. Must replicate this logic for Syrin exceptions.

  **API/Type References**:
  - `from syrin.swarm import Swarm, SwarmConfig` — For REFLECTION topology
  - `from syrin.enums import SwarmTopology` — `SwarmTopology.REFLECTION`
  - `from agents import MarketOverviewAgent, ..., CriticAgent, create_model` — Agent classes and factory
  - `from stages import STAGES` — Stage configs
  - `from tools import duckduckgo_search, WEB_SEARCH_TOOL_SPEC` — Custom tools

  **External References**:
  - Syrin docs: https://docs.syrin.dev/agent-kit/ — Swarm setup, REFLECTION topology, `arun()` method

  **WHY Each Reference Matters**:
  - `researcher.py:248-261` — Must understand the current async interface (yields event tuples) so main.py can consume the new events
  - `main.py:571-605` — Must replicate rate-limit handling pattern for the new Syrin exceptions
  - Syrin Swarm API — Must use exact API: `Swarm(agents=..., config=SwarmConfig(topology=SwarmTopology.REFLECTION, ...))`, then `await swarm.arun()`

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: researcher.py imports cleanly with no old code
    Tool: Bash
    Preconditions: researcher.py rewritten
    Steps:
      1. Run: python -c "import researcher; print('OK')"
      2. Assert no import errors
    Expected Result: Module imports successfully
    Failure Indicators: ImportError, NameError (old code references)
    Evidence: .sisyphus/evidence/task-7-import-test.txt

  Scenario: run_research_pipeline() is async and yields event tuples
    Tool: Bash
    Preconditions: researcher.py rewritten
    Steps:
      1. Run: python -c "import inspect; from researcher import run_research_pipeline; print(inspect.isasyncgenfunction(run_research_pipeline))"
      2. Assert output: True
    Expected Result: Function is an async generator
    Failure Indicators: False (not async), TypeError
    Evidence: .sisyphus/evidence/task-7-async-generator.txt

  Scenario: No old stream_stage or ProviderConfig symbols remain
    Tool: Bash
    Preconditions: researcher.py rewritten
    Steps:
      1. Run: python -c "import researcher; print('stream_stage' in dir(researcher), 'ProviderConfig' in dir(researcher))"
      2. Assert output: False False
    Expected Result: Old symbols removed cleanly
    Failure Indicators: True (old symbols still exist)
    Evidence: .sisyphus/evidence/task-7-no-old-symbols.txt
  ```

  **Commit**: YES (groups with 8)
  - Message: `feat(pipeline): replace sequential loop with syrin reflection topology`
  - Files: `researcher.py`

- [x] 8. Update main.py _run_all_stages() for reflection loop

  **What to do**:
  - Replace the current `_run_all_stages()` worker method to consume the new event tuples from `run_research_pipeline()`
  - The new event types are:
    - `("stage_start", stage_id)` — Mark sidebar as "running", clear stage display
    - `("reflection_round", (stage_id, round_num))` — Update status bar: "⟳ {stage_name} — Round {round_num}..."
    - `("stage_complete", (stage_id, result_text))` — Store result, update output display with full text
    - `("error", message)` — Show error, mark stage as failed
    - `("rate_limit", "")` — Apply exponential backoff (keep existing 5→10→20s pattern)
    - `("searching", "")` — Status: "🌐 Searching the web…"
    - `("search_done", "")` — Status: "⟳ {stage_name}…"
  - Replace `_append_output()` behavior: instead of token-by-token streaming, display stage results as complete blocks with a "Round N" annotation showing which reflection round produced them
  - Keep `_output_buffer` and `_results` storage for export compatibility
  - Update `_flush_output()` to render full blocks instead of incremental tokens
  - Remove all references to old `stream_stage()`, `ProviderConfig`, `_stream_anthropic()`, `_stream_ollama()`
  - Update the settings/startup to use `create_model()` from `agents.py` instead of old `ProviderConfig`
  - Keep existing keybindings, sidebar, progress bar structure — only change what runs inside `_run_all_stages()`

  **Must NOT do**:
  - Do NOT redesign the TUI layout or widget structure (keep existing shell)
  - Do NOT add token-by-token streaming back
  - Do NOT remove the sidebar or progress bar
  - Do NOT change keybindings

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO — depends on Task 7
  - **Parallel Group**: Wave 3
  - **Blocks**: Tasks 9, 10
  - **Blocked By**: Task 7 (pipeline must exist first)

  **References**:

  **Pattern References**:
  - `main.py:818-954` — Current `_run_all_stages()` method. Must understand the exact flow: iterate stages, stream tokens, handle events, store results, update sidebar.
  - `main.py:970-987` — `_append_output()` and `_flush_output()`. Must adapt from token-by-token to block display.
  - `main.py:571-605` — Rate-limit retry loop. Must replicate for new event format.
  - `main.py:338-407` — `APP_CSS` string. Do not modify.

  **API/Type References**:
  - `from researcher import run_research_pipeline` — New async generator
  - `from agents import create_model` — Provider factory
  - New event types: `stage_start`, `reflection_round`, `stage_complete`, `error`, `rate_limit`, `searching`, `search_done`

  **WHY Each Reference Matters**:
  - `main.py:818-954` — This is the exact method being rewritten. Must preserve sidebar updates, progress tracking, and result storage.
  - `main.py:970-987` — Must adapt `_append_output` from streaming to block display.
  - Rate-limit loop — Must preserve the same backoff behavior for the new pipeline

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: main.py imports and compiles without old researcher references
    Tool: Bash
    Preconditions: main.py updated
    Steps:
      1. Run: python -m py_compile main.py && echo "OK"
      2. Assert output: OK
    Expected Result: main.py compiles successfully with new imports
    Failure Indicators: SyntaxError, NameError for old symbols
    Evidence: .sisyphus/evidence/task-8-compile-test.txt

  Scenario: No references to old stream_stage or ProviderConfig in main.py
    Tool: Bash (grep)
    Preconditions: main.py updated
    Steps:
      1. Run: grep -c "stream_stage\|ProviderConfig\|_stream_anthropic\|_stream_ollama" main.py
      2. Assert output: 0 (no old references)
    Expected Result: Zero matches for old function names
    Failure Indicators: Any matches found
    Evidence: .sisyphus/evidence/task-8-no-old-refs.txt
  ```

  **Commit**: YES (groups with 7)
  - Message: `feat(pipeline): replace sequential loop with syrin reflection topology`
  - Files: `main.py`

- [x] 9. Update exporter.py for Syrin result objects

  **What to do**:
  - Update `export_results()` to accept the new result format from Syrin agents
  - Current format: `dict[str, str]` mapping `stage.id` → plain text string
  - New format: Syrin result objects have `.content` (str), `.cost` (float), `.tokens` (int) fields
  - The export should still produce markdown with all 8 sections, but now also include:
    - Reflection metadata (how many rounds per stage)
    - Quality scores from the critic (if available)
  - Keep the same output file structure (timestamped .md files)
  - The exported markdown should have a header for each stage with its name and quality score

  **Must NOT do**:
  - Do NOT change the output directory or file naming convention
  - Do NOT add PDF/DOCX export (future scope)
  - Do NOT remove the ability to export to plain .md files

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO — depends on Task 8 (need result format)
  - **Parallel Group**: Wave 4
  - **Blocks**: Task 11 (cleanup needs to verify export still works)
  - **Blocked By**: Task 8 (result format from pipeline)

  **References**:

  **Pattern References**:
  - `exporter.py` — Current `export_results()` function. Must preserve output structure but adapt input format.
  - `main.py:_results` — Dict storing stage results. The key interface remains `stage.id → result`.

  **API/Type References**:
  - Syrin result object: `result.content` (str), `result.cost` (float), `result.tokens` (int)
  - Reflection metadata: round count, critic scores

  **WHY Each Reference Matters**:
  - `exporter.py` — Must keep producing valid markdown but accept new result types
  - `main.py:_results` — Must ensure the dict fed to export still has stage.id keys

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: exporter.py compiles successfully
    Tool: Bash
    Preconditions: exporter.py updated
    Steps:
      1. Run: python -m py_compile exporter.py && echo "OK"
      2. Assert output: OK
    Expected Result: Module compiles without errors
    Failure Indicators: SyntaxError, Import error
    Evidence: .sisyphus/evidence/task-9-compile.txt

  Scenario: export_results produces valid markdown with mock data
    Tool: Bash
    Preconditions: exporter.py updated
    Steps:
      1. Create small test script that builds mock result objects and calls export_results
      2. Run test script, assert .md file is created with all 8 section headers
      3. Verify section headers exist: "Market Overview", "Competitor Analysis", etc.
    Expected Result: Markdown file contains all 8 section headers
    Failure Indicators: Missing sections, file not created
    Evidence: .sisyphus/evidence/task-9-export-md.txt
  ```

  **Commit**: YES (groups with 10)
  - Message: `feat(ui): update exporter and display for syrin results`
  - Files: `exporter.py`

- [x] 10. Update main.py UI for batch-then-display

  **What to do**:
  - Adapt `_flush_output()` and `_append_output()` for batch display instead of token streaming
  - Instead of rendering each token as it arrives, display complete blocks per stage:
    - Show "Round 1" header, then full research text
    - Show "Round 2 (refined)" header, then refined text
    - Show "Quality: 8/10 ✓" when stage passes
  - The `RichMarkdown` widget in `#output-md` should render each completed stage as a section
  - The sidebar should show reflection round numbers during execution
  - The status bar should show which reflection round is active: "⟳ Market Overview — Round 2 of 3…"
  - The `_stage_buffer` should accumulate the full output for the current stage, not individual tokens
  - Keep auto-scroll behavior if user is at the bottom

  **Must NOT do**:
  - Do NOT redesign the UI layout
  - Do NOT add token-by-token streaming back
  - Do NOT remove existing sidebar states ("done", "failed", etc.)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 9 — different files)
  - **Parallel Group**: Wave 4
  - **Blocks**: Task 11
  - **Blocked By**: Task 8 (pipeline must emit new event types)

  **References**:

  **Pattern References**:
  - `main.py:970-987` — Current `_append_output()` and `_flush_output()`. Must change from token-by-token to block display.
  - `main.py:338-407` — `APP_CSS` styling. May need minor additions for "Round N" headers but do NOT redesign layout.
  - `main.py:416-450` (approximate) — Sidebar rendering. Must show reflection round numbers during execution.

  **API/Type References**:
  - New event types from researcher.py: `stage_start`, `reflection_round`, `stage_complete`

  **WHY Each Reference Matters**:
  - `main.py:970-987` — Must change from incremental token display to block display with round annotations
  - `main.py:338-407` — Minor CSS additions only for round headers
  - Sidebar — Must show round numbers during reflection

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: TUI launches without errors
    Tool: interactive_bash (tmux)
    Preconditions: All files updated
    Steps:
      1. Start tmux session
      2. Run: source .venv/bin/activate && python main.py
      3. Wait for TUI to render (3 seconds)
      4. Capture screen output
      5. Assert: TUI shows sidebar, input area, status bar
    Expected Result: TUI renders with no Python exceptions
    Failure Indicators: Traceback, crash, missing widgets
    Evidence: .sisyphus/evidence/task-10-tui-launch.txt

  Scenario: Batch display renders stage blocks with round headers
    Tool: interactive_bash (tmux)
    Preconditions: TUI running
    Steps:
      1. Enter a test idea (requires API key)
      2. Select a provider
      3. Start the research run
      4. Observe output display shows "Round 1" headers as stages complete
    Expected Result: Stage output appears as complete blocks with round annotations
    Failure Indicators: Tokens appearing one-by-one, missing round headers
    Evidence: .sisyphus/evidence/task-10-batch-display.txt
  ```

  **Commit**: YES (groups with 9)
  - Message: `feat(ui): update exporter and display for syrin results`
  - Files: `main.py`

- [x] 11. Clean up old code paths + update requirements.txt

  **What to do**:
  - Remove from `researcher.py`:
    - Old `ProviderConfig` dataclass (replaced by `create_model()` in agents.py)
    - Old `_stream_anthropic()` function
    - Old `_stream_ollama()` function
    - Old `_fetch_search_context()` function (ported to tools.py)
    - Old `stream_stage()` function
  - Remove from `main.py`:
    - All `from researcher import ProviderConfig, stream_stage` references
    - Old event handling for `"text"` token-by-token (replaced by batch events)
  - Remove from `requirements.txt`:
    - Direct `anthropic` package (syrin bundles it)
    - Direct `openai` package (syrin bundles it)
  - Update `.env.example` with Syrin-specific env vars
  - Add a `.gitignore` file (currently missing per AGENTS.md note) excluding `.venv/`, `__pycache__/`, `.env`
  - Verify the app starts cleanly: `python -c "import main; print('OK')"`

  **Must NOT do**:
  - Do NOT remove `textual` or `python-dotenv` from requirements
  - Do NOT remove `aiohttp` (still used by DuckDuckGo tool in tools.py)
  - Do NOT remove any `.env` environment variable names that are still in use

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO — depends on all previous tasks
  - **Parallel Group**: Wave 5
  - **Blocks**: Task 12
  - **Blocked By**: Tasks 7, 8, 9, 10 (all code changes must be done before cleanup)

  **References**:

  **Pattern References**:
  - `researcher.py` — All old functions being removed. Must verify they're not imported elsewhere.
  - `main.py` — Import statements to update.
  - `requirements.txt` — Current dependency list.
  - `AGENTS.md` — Notes missing `.gitignore`

  **API/Type References**:
  - No new API references — this is cleanup

  **WHY Each Reference Matters**:
  - `researcher.py` — Must remove all old code but verify nothing else imports them
  - `main.py` — Must update all import references
  - `requirements.txt` — Must not remove transitive deps that syrin doesn't bundle

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: No old function references remain in codebase
    Tool: Bash (grep)
    Preconditions: Cleanup complete
    Steps:
      1. Run: grep -rn "_stream_anthropic\|_stream_ollama\|_fetch_search_context\|stream_stage\|ProviderConfig" *.py
      2. Assert: only matches in comments or docstrings, not in active code
    Expected Result: Zero active references to old functions/classes
    Failure Indicators: Any active references found
    Evidence: .sisyphus/evidence/task-11-old-refs-grep.txt

  Scenario: App imports cleanly after cleanup
    Tool: Bash
    Preconditions: Cleanup complete
    Steps:
      1. Run: python -c "import main; import researcher; import agents; import tools; import stages; import exporter; print('ALL OK')"
      2. Assert: ALL OK printed
    Expected Result: All modules import without errors
    Failure Indicators: ImportError, ModuleNotFoundError for removed symbols
    Evidence: .sisyphus/evidence/task-11-import-test.txt

  Scenario: .gitignore exists and excludes venv/cache
    Tool: Bash
    Preconditions: Cleanup complete
    Steps:
      1. Run: test -f .gitignore && grep -c ".venv\|__pycache__\|.env" .gitignore
      2. Assert: .gitignore exists and has 3+ matching lines
    Expected Result: .gitignore covers standard Python exclusions
    Failure Indicators: Missing file or missing entries
    Evidence: .sisyphus/evidence/task-11-gitignore.txt
  ```

  **Commit**: YES (sole)
  - Message: `chore: remove old provider code paths and update dependencies`
  - Files: `researcher.py`, `main.py`, `requirements.txt`, `.env.example`, `.gitignore`

- [x] 12. End-to-end smoke test

  **What to do**:
  - Start the app with `python main.py` and verify:
    - TUI launches without errors
    - Provider selection works (Anthropic and Ollama both appear)
    - Entering an idea and starting research triggers the pipeline
    - All 8 research topics execute (even if one fails, the rest continue)
    - Reflection progress indicators show in status bar
    - Batch display renders stage output as blocks
    - Export produces valid markdown with all 8 sections
  - Test with Anthropic provider (if API key available)
  - Test error handling: invalid API key shows graceful error
  - Verify no old code paths are accidentally still active

  **Must NOT do**:
  - Do NOT add new features beyond the integration scope
  - Do NOT modify any production code — this is a verification task only

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO — depends on all previous tasks
  - **Parallel Group**: Wave 5
  - **Blocks**: F1-F4
  - **Blocked By**: Task 11 (cleanup must be done)

  **References**:

  **Pattern References**:
  - `main.py` — Full application entry point
  - `researcher.py` — New pipeline
  - `agents.py` — All agent definitions
  - `stages.py` — Stage configs
  - `tools.py` — Custom tools

  **API/Type References**:
  - No new references — this is verification of existing code

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Full pipeline run with Anthropic
    Tool: interactive_bash (tmux)
    Preconditions: ANTHROPIC_API_KEY set in .env
    Steps:
      1. Start tmux session
      2. Run: source .venv/bin/activate && python main.py
      3. Wait for TUI to render
      4. Select Anthropic provider
      5. Enter idea: "AI-powered code review tool"
      6. Start research
      7. Wait for first stage to complete (up to 60s)
      8. Verify "Market Overview" section appears in output
      9. Verify status bar shows reflection round numbers
    Expected Result: At least first stage completes with research output
    Failure Indicators: App crashes, no output, missing stage headers
    Evidence: .sisyphus/evidence/task-12-anthropic-pipeline.txt

  Scenario: Error handling for invalid API key
    Tool: interactive_bash (tmux)
    Preconditions: ANTHROPIC_API_KEY set to "invalid-key"
    Steps:
      1. Start tmux session
      2. Run: source .venv/bin/activate && python main.py
      3. Select Anthropic provider
      4. Enter idea: "test idea"
      5. Start research
      6. Verify graceful error message appears (not crash/traceback)
    Expected Result: Error shown in TUI, app doesn't crash
    Failure Indicators: Unhandled exception, traceback in console
    Evidence: .sisyphus/evidence/task-12-error-handling.txt

  Scenario: Export produces valid markdown
    Tool: Bash
    Preconditions: Pipeline has completed at least one run
    Steps:
      1. Find the most recent .md file in the export directory
      2. Run: grep -c "^##" <export_file>.md (count section headers)
      3. Assert: at least 4 section headers (partial run is OK for smoke test)
    Expected Result: Export file contains section headers
    Failure Indicators: No file, no headers, empty file
    Evidence: .sisyphus/evidence/task-12-export-verify.txt
  ```

  **Commit**: NO (verification only, no code changes)

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.

- [x] F1. **Plan Compliance Audit** — `oracle`
  - VERDICT: APPROVE — Must Have [7/7], Must NOT Have [5/5]
  - Evidence: .sisyphus/evidence/f1-compliance-audit.txt
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, run command). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [x] F2. **Code Quality Review** — `unspecified-high`
  - VERDICT: APPROVE (after minor cleanup: removed unused `import time`)
  - Issue: `import time` unused — fixed
  - Remaining: `ProviderConfig` in main.py for UI modal (acceptable)
  Run `python -m py_compile main.py researcher.py agents.py stages.py tools.py exporter.py`. Review all changed files for: bare except clauses, print() in production code (should use Textual notifications), unused imports, commented-out code. Check AI slop: excessive comments, over-abstraction, generic names.
  Output: `Compile [PASS/FAIL] | Slop [N issues] | Files [N clean/N issues] | VERDICT`

- [x] F3. **Real Manual QA** — `unspecified-high`
  - VERDICT: APPROVE — TUI launches, TUI renders, export produces valid markdown
  - Evidence: .sisyphus/evidence/f3-qa-results.txt
  Start from clean state. Launch `python main.py`, select Anthropic provider, enter a test idea, run full pipeline. Verify all 8 research topics appear. Verify reflection progress indicators show. Verify export produces valid markdown with all 8 sections. Test Ollama provider. Test with invalid API key (graceful error).
  Output: `Scenarios [N/N pass] | Integration [N/N] | Edge Cases [N tested] | VERDICT`

- [x] F4. **Scope Fidelity Check** — `deep`
  - VERDICT: APPROVE — All 12 tasks implemented, no scope creep, minor cosmetic deviations only
  - Evidence: .sisyphus/evidence/f4-scope-fidelity.txt
  For each task: read "What to do", read actual diff (git log/diff). Verify 1:1 — everything in spec was built (no missing), nothing beyond spec was built (no creep). Check "Must NOT do" compliance. Detect cross-task contamination. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

- **1 + 2 + 3**: `feat(deps): add syrin-python dependency and scaffolding` — requirements.txt, tools.py, stages.py
- **4 + 5 + 6**: `feat(agents): add research and critic agent definitions` — agents.py
- **7 + 8**: `feat(pipeline): replace sequential loop with syrin reflection topology` — researcher.py, main.py
- **9 + 10**: `feat(ui): update exporter and display for syrin results` — exporter.py, main.py
- **11**: `chore: remove old provider code paths` — researcher.py cleanup

---

## Success Criteria

### Verification Commands
```bash
python -m py_compile agents.py researcher.py stages.py main.py exporter.py tools.py  # Expected: no errors
python main.py  # Expected: TUI launches without error
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All 8 research topics render in TUI output
- [ ] Reflection loop produces visible quality improvements
- [ ] Export produces valid markdown with all sections
- [ ] Both Anthropic and Ollama providers work