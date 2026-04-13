"""Syrin-powered research pipeline for Prode.

Runs each research stage through a producer-critic reflection loop by calling
Syrin agents directly (bypassing Swarm), so that any API or agent error is
surfaced as an "error" event rather than silently returning empty content.
"""

import re
from typing import AsyncGenerator, TypedDict

# Re-export ProviderConfig for backward compat with config.py
from dataclasses import dataclass
from typing import Optional


@dataclass
class ProviderConfig:
    """Provider configuration — mirrors the original researcher.py interface."""

    provider: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: str = ""

    @property
    def display_name(self) -> str:
        """Human-readable label for the header bar, e.g. 'Ollama · qwen3.5:397b'."""
        name = self.provider.capitalize()
        if self.model:
            name = f"{name} · {self.model}"
        return name


from agents import (
    MarketOverviewAgent,
    CompetitorAnalysisAgent,
    PainPointsAgent,
    ICPAgent,
    SizingAgent,
    FeaturesAgent,
    PositioningAgent,
    VerdictAgent,
    CriticAgent,
    create_model,
)
from stages import STAGES


class StageResult(TypedDict):
    stage_id: str
    content: str
    rounds_completed: int
    score: float | None


PipelineEvent = tuple[
    str,  # event type
    str | tuple[str, int] | StageResult,  # payload
]


AGENT_CLASSES = {
    "market": MarketOverviewAgent,
    "competitors": CompetitorAnalysisAgent,
    "pain_points": PainPointsAgent,
    "icp": ICPAgent,
    "sizing": SizingAgent,
    "features": FeaturesAgent,
    "positioning": PositioningAgent,
    "verdict": VerdictAgent,
}


def _extract_score(text: str) -> float:
    """Extract a numeric quality score in [0, 1] from critic output.

    Prefers a number following a 'Score:' keyword; falls back to the last
    decimal in [0, 1] found anywhere in the text; defaults to 0.5.
    """
    score_kw = re.search(r"[Ss]core\s*[:\-]?\s*(\d+(?:\.\d+)?)", text)
    if score_kw:
        return max(0.0, min(1.0, float(score_kw.group(1))))
    candidates = [
        float(m.group(1))
        for m in re.finditer(r"\b(\d+\.\d+)\b", text)
        if 0.0 <= float(m.group(1)) <= 1.0
    ]
    return candidates[-1] if candidates else 0.5


async def run_research_pipeline(
    idea: str,
    provider: str,
    model: str,
    api_key: str | None = None,
    base_url: str | None = None,
) -> AsyncGenerator[PipelineEvent, None]:
    """Run the full 8-stage research pipeline with per-stage reflection.

    Each stage runs a producer agent followed by a critic agent.  If the
    critic scores the output >= 0.7, the stage completes early; otherwise
    the producer receives the critic's feedback and tries again, up to
    ``stage.max_reflection_rounds`` total rounds.

    Errors from agent calls propagate immediately as ``("error", message)``
    events so no stage failure can be silently swallowed.

    Yields:
        - ``("stage_start",    stage_id)``
        - ``("reflection_round", (stage_id, round_num))``  — 0-based, real-time
        - ``("stage_complete", StageResult)``
        - ``("error",          message)``
    """
    for stage in STAGES:
        yield ("stage_start", stage.id)

        best_content: str = ""
        best_score: float = 0.0
        critic_feedback: str = ""
        rounds_done: int = 0

        try:
            producer_cls = AGENT_CLASSES[stage.id]
            producer_system = producer_cls.system_prompt.format(idea=idea)

            for round_idx in range(stage.max_reflection_rounds):
                # Fresh model per round — avoids any internal async-session
                # or conversation-history state leaking across rounds.
                producer_model = create_model(
                    provider=provider,
                    model=model,
                    api_key=api_key,
                    base_url=base_url,
                )

                producer_input = (
                    f"Research: {stage.id} for idea: {idea}"
                    if round_idx == 0
                    else (
                        f"Research: {stage.id} for idea: {idea}"
                        f"\n\nPrevious critic feedback:\n{critic_feedback}"
                    )
                )

                producer = producer_cls(
                    model=producer_model,
                    provider=provider,
                    system_prompt=producer_system,
                )

                try:
                    producer_resp = await producer.arun(producer_input)
                    content = getattr(producer_resp, "content", "") or ""
                except Exception as exc:
                    yield (
                        "error",
                        f"[{stage.id}] Round {round_idx + 1} producer failed: {exc}",
                    )
                    break  # Stop refining, use best content so far

                if not content:
                    # Producer returned nothing — stop refining, use best so far
                    break

                # Critic evaluates the output
                critic_model = create_model(
                    provider=provider,
                    model=model,
                    api_key=api_key,
                    base_url=base_url,
                )
                critic = CriticAgent(model=critic_model, threshold=0.7)

                try:
                    critic_resp = await critic.arun(content)
                    critic_feedback = getattr(critic_resp, "content", "") or ""
                    score = _extract_score(critic_feedback)
                except Exception as exc:
                    # Critic failed — still keep the producer's output as the
                    # best result for this stage, but skip further rounds.
                    yield (
                        "error",
                        f"[{stage.id}] Round {round_idx + 1} critic failed: {exc}",
                    )
                    best_content = content
                    rounds_done = round_idx + 1
                    break

                rounds_done = round_idx + 1
                best_content = content
                best_score = score

                # Emit round event in real-time (not post-hoc)
                yield ("reflection_round", (stage.id, round_idx))

                if score >= 0.7:
                    break  # Quality threshold met — no need for further rounds

        except Exception as exc:
            yield ("error", f"[{stage.id}] {stage.name} setup failed: {exc}")

        # Always yield stage_complete so that the results dict is populated
        # (even with empty content) and the export doesn't show
        # "Stage not completed." for stages that partially ran.
        yield (
            "stage_complete",
            {
                "stage_id": stage.id,
                "content": best_content,
                "rounds_completed": rounds_done,
                "score": best_score if rounds_done > 0 else None,
            },
        )
