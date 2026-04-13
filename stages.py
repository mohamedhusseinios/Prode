"""Stage definitions for the product research pipeline.

Migrated from Stage (prompt_template) to StageConfig (agent_class_path).
The prompt_template strings are preserved as comments for reference during migration.
They will be removed in the cleanup task (T11).
"""

from dataclasses import dataclass


@dataclass
class StageConfig:
    """Configuration for a research pipeline stage.

    Attributes:
        id: Unique stage identifier (used as dict key and sidebar marker).
        name: Full display name for the output section header.
        short_name: Abbreviated name for the sidebar.
        agent_class_path: Dotted path to the Agent subclass (e.g. "agents.MarketOverviewAgent").
        max_reflection_rounds: Maximum producer-critic-refine cycles (default 2, max 3).
        description: Plain-language description of what this stage investigates.
    """

    id: str
    name: str
    short_name: str
    agent_class_path: str
    max_reflection_rounds: int = 2
    description: str = ""


# prompt_template strings preserved here as comments for reference.
# Original Stage dataclass had prompt_template: str on each stage.
# Agent system_prompts in agents.py are adapted from these templates.
#
# Example (market):
# prompt_template="""Conduct a comprehensive market overview for this product idea: **{idea}**
# Cover:
# 1. **Problem Space**: What core problem does this solve? How painful is it?
# 2. **Market Maturity**: Early-stage, growing, mature, or declining? Provide evidence.
# ...


STAGES = [
    StageConfig(
        id="market",
        name="Market Overview",
        short_name="Market",
        agent_class_path="agents.MarketOverviewAgent",
        max_reflection_rounds=2,
        description="Problem space, market maturity, existing category, key trends, regulatory landscape, geographic distribution.",
    ),
    StageConfig(
        id="competitors",
        name="Competitor Analysis",
        short_name="Compete",
        agent_class_path="agents.CompetitorAnalysisAgent",
        max_reflection_rounds=2,
        description="5-8 competitors in a table: pricing, strengths, weaknesses, funding, market leader, white space.",
    ),
    StageConfig(
        id="pain_points",
        name="Customer Pain Points",
        short_name="Pain Pts",
        agent_class_path="agents.PainPointsAgent",
        max_reflection_rounds=2,
        description="Top frustrations with current solutions, emotional & economic pain, unmet needs, paraphrased quotes.",
    ),
    StageConfig(
        id="icp",
        name="ICP Definition",
        short_name="ICP",
        agent_class_path="agents.ICPAgent",
        max_reflection_rounds=2,
        description="2-3 ideal customer profiles: role, goals, trigger events, WTP, success metric.",
    ),
    StageConfig(
        id="sizing",
        name="Market Sizing",
        short_name="Sizing",
        agent_class_path="agents.SizingAgent",
        max_reflection_rounds=2,
        description="TAM/SAM/SOM via bottom-up and top-down methodology, key assumptions.",
    ),
    StageConfig(
        id="features",
        name="Feature Prioritization",
        short_name="Features",
        agent_class_path="agents.FeaturesAgent",
        max_reflection_rounds=2,
        description="MoSCoW table (15-20 features), MVP scope, hardest technical challenge.",
    ),
    StageConfig(
        id="positioning",
        name="Positioning Angles",
        short_name="Position",
        agent_class_path="agents.PositioningAgent",
        max_reflection_rounds=2,
        description="3 differentiation strategies, hero copy, recommended angle, brand voice.",
    ),
    StageConfig(
        id="verdict",
        name="Verdict",
        short_name="Verdict",
        agent_class_path="agents.VerdictAgent",
        max_reflection_rounds=2,
        description="Go/No-Go score (1-10), scoring table, bull/bear case, critical assumptions, next steps.",
    ),
]
