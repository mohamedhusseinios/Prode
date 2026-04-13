"""Syrin-powered research pipeline for Prode.

This module replaces the old researcher.py (stream_stage, _stream_anthropic,
_stream_ollama, _fetch_search_context, ProviderConfig). It uses Syrin's Swarm
REFLECTION topology to run each research topic through a producer-critic loop.
"""

import asyncio
import os
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


from syrin import Model
from syrin.swarm import Swarm, SwarmConfig, ReflectionConfig
from syrin.enums import SwarmTopology

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


def _build_swarm(
    stage_id: str,
    idea: str,
    model: Model,
    provider: str,
    max_rounds: int,
) -> Swarm:
    """Build a single-stage REFLECTION swarm for one research topic."""
    producer_cls = AGENT_CLASSES[stage_id]

    # Inject idea into producer system prompt
    producer_system = producer_cls.system_prompt.format(idea=idea)

    producer = producer_cls(
        model=model,
        provider=provider,
        system_prompt=producer_system,
    )
    critic = CriticAgent(
        model=model,
        threshold=7,
    )

    # Create factory callables with pre-bound args for ReflectionConfig.
    # These must be zero-arg callables that return agent instances, and must have
    # a __name__ attribute for the swarm's agent-status tracking.
    producer_factory = _agent_factory(
        producer_cls,
        __name__=producer_cls.__name__,
        model=model,
        provider=provider,
        system_prompt=producer_system,
    )
    critic_factory = _agent_factory(
        CriticAgent, __name__=CriticAgent.__name__, model=model, threshold=7
    )

    return Swarm(
        agents=[producer, critic],
        goal=f"Research: {stage_id} for idea: {idea}",
        config=SwarmConfig(
            topology=SwarmTopology.REFLECTION,
            reflection=ReflectionConfig(
                producer=producer_factory,
                critic=critic_factory,
                max_rounds=max_rounds,
                stop_when=lambda ro: ro.score >= 0.7,
            ),
        ),
    )


def _agent_factory(cls, __name__: str, **kwargs):
    """Create a zero-arg callable that instantiates ``cls(**kwargs)``.

    The returned callable carries a ``__name__`` attribute so that
    ``syrin.swarm`` can use it for agent-status tracking.
    """

    def factory():
        return cls(**kwargs)

    factory.__name__ = __name__
    return factory


async def run_research_pipeline(
    idea: str,
    provider: str,
    model: str,
    api_key: str | None = None,
    base_url: str | None = None,
) -> AsyncGenerator[PipelineEvent, None]:
    """Run the full 8-stage research pipeline with reflection.

    Args:
        idea: The product idea to research.
        provider: "anthropic", "ollama", or "custom".
        model: Model name string.
        api_key: Optional API key (falls back to env vars).
        base_url: Optional base URL for Ollama/custom endpoints.

    Yields:
        PipelineEvent tuples:
        - ("stage_start", stage_id)
        - ("reflection_round", (stage_id, round_num))   # 0-based round index
        - ("stage_complete", StageResult)  # StageResult = {content, rounds_completed, score}
        - ("error", message)
        - ("searching", "")
        - ("search_done", "")
    """
    syrin_model = create_model(
        provider=provider,
        model=model,
        api_key=api_key,
        base_url=base_url,
    )

    for stage in STAGES:
        yield ("stage_start", stage.id)

        try:
            swarm = _build_swarm(
                stage_id=stage.id,
                idea=idea,
                model=syrin_model,
                provider=provider,
                max_rounds=stage.max_reflection_rounds,
            )

            # Run reflection rounds and yield round progress
            handle = swarm.play()
            # wait() returns SwarmResult when the swarm completes
            result = await handle.wait()

            if result.reflection_result is None:
                yield ("error", f"{stage.name}: no reflection result returned")
                continue

            rr = result.reflection_result

            # Yield each completed round for UI feedback
            for ro in rr.round_outputs:
                yield ("reflection_round", (stage.id, ro.round_index))

            final_content = rr.content
            final_score = (
                rr.round_outputs[rr.final_round].score if rr.round_outputs else None
            )

            yield (
                "stage_complete",
                {
                    "content": final_content,
                    "rounds_completed": rr.rounds_completed,
                    "score": final_score,
                },
            )

        except Exception as exc:
            yield ("error", f"{stage.name} failed: {exc}")
