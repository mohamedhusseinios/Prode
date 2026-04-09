"""Stage definitions for the product research pipeline."""

from dataclasses import dataclass


@dataclass
class Stage:
    id: str
    name: str
    short_name: str
    prompt_template: str


STAGES = [
    Stage(
        id="market",
        name="Market Overview",
        short_name="Market",
        prompt_template="""Conduct a comprehensive market overview for this product idea: **{idea}**

Cover:
1. **Problem Space**: What core problem does this solve? How painful is it?
2. **Market Maturity**: Early-stage, growing, mature, or declining? Provide evidence.
3. **Existing Category**: What product category does this fit into?
4. **Key Trends**: 3-5 trends shaping this market right now (with data points).
5. **Regulatory Landscape**: Any relevant regulations or compliance requirements?
6. **Geographic Distribution**: Where is this market most developed?

Use current market data. Be specific with numbers and dates.""",
    ),
    Stage(
        id="competitors",
        name="Competitor Analysis",
        short_name="Compete",
        prompt_template="""Identify and analyze 5-8 direct and indirect competitors for: **{idea}**

Create a competitor table:

| Company | Founded | Pricing | Target Customer | Key Strengths | Key Weaknesses |
|---------|---------|---------|-----------------|---------------|----------------|

Then provide:
- **Market Leader**: Who dominates and why?
- **Competitive Dynamics**: Winner-take-all or fragmented?
- **White Space**: Gaps no one fills well?
- **Funding Landscape**: Well-funded players, recent exits?

Use real company names and real pricing tiers.""",
    ),
    Stage(
        id="pain_points",
        name="Customer Pain Points",
        short_name="Pain Pts",
        prompt_template="""Research the top customer pain points for people currently trying to solve: **{idea}**

Provide:
1. **Top 7 Pain Points**: Ranked by severity (cite reviews, Reddit, G2, Capterra where possible).
2. **Emotional Pain**: What do customers feel when their current solution fails?
3. **Economic Pain**: Time/money/resources lost to the problem.
4. **Workflow Friction**: Where do current tools break down?
5. **Unmet Needs**: Needs that NO current solution addresses well.
6. **Paraphrased Quotes**: 3-5 that capture the frustration.

Be specific and cite sources where possible.""",
    ),
    Stage(
        id="icp",
        name="ICP Definition",
        short_name="ICP",
        prompt_template="""Define 2-3 detailed Ideal Customer Profiles for: **{idea}**

For each ICP:

**Profile [N]: [Descriptive Name]**
- **Role/Title**:
- **Company Profile**: Size, industry, stage
- **Primary Goals**: What are they trying to achieve?
- **Current Solution**: What tool/process do they use today?
- **Trigger Events**: What would make them seek a new solution?
- **Buying Process**: Who has authority? How long is the sales cycle?
- **Willingness to Pay**: Monthly budget range for this type of tool
- **Success Metric**: How would they measure success?

Make these specific enough to find these people on LinkedIn.""",
    ),
    Stage(
        id="sizing",
        name="Market Sizing",
        short_name="Sizing",
        prompt_template="""Estimate the market size for: **{idea}**

Use both bottom-up and top-down approaches:

**Bottom-Up:**
- How many potential buyers exist? Show the math.
- Average contract value (ACV) or monthly price point?
- Buyers × ACV = Revenue potential

**Top-Down:**
- Total industry spend this sits within?
- Realistic addressable percentage?

Provide:
- **TAM** (Total Addressable Market): Full global opportunity with methodology
- **SAM** (Serviceable Addressable Market): Portion realistically serveable
- **SOM** (Serviceable Obtainable Market): Capturable in years 1-5

**Key Assumptions**: List 3-5 assumptions that drive your estimates.
Use proxy data and cite sources where available.""",
    ),
    Stage(
        id="features",
        name="Feature Prioritization",
        short_name="Features",
        prompt_template="""Define the MVP feature set for: **{idea}**

Create a MoSCoW prioritization table (include 15-20 features):

| Feature | Priority (M/S/C/W) | User Impact (H/M/L) | Build Effort (H/M/L) | Notes |
|---------|-------------------|---------------------|----------------------|-------|

Then provide:
1. **MVP Scope**: Exactly what ships in v1 (Must-haves only) — 2-3 sentences.
2. **The One Feature**: If you could ship only ONE thing, what and why?
3. **Features to Cut**: 5 features that seem important but shouldn't be in v1 (with reasoning).
4. **Hardest Technical Challenge**: What's the riskiest thing to build?
5. **Time Estimate**: Rough timeline for a 2-3 person team to ship MVP.""",
    ),
    Stage(
        id="positioning",
        name="Positioning Angles",
        short_name="Position",
        prompt_template="""Develop 3 distinct positioning strategies for: **{idea}**

For each angle:

**Angle [N]: [Memorable Name]**
- **Core Claim**: One sentence value proposition.
- **Target Audience**: Which ICP resonates most?
- **Category Frame**: What category are you defining or redefining?
- **Landing Page Hero**: Draft H1 + subheadline (2-3 sentences).
- **Proof Points**: 3 concrete things that make this claim believable.
- **Competitive Wedge**: Who does this positioning hurt most?

End with:
- **Recommended Angle**: Which to lead with and why.
- **Messaging Hierarchy**: How to sequence for different audiences.
- **Brand Voice**: 3 adjectives that define the brand personality.""",
    ),
    Stage(
        id="verdict",
        name="Verdict",
        short_name="Verdict",
        prompt_template="""Provide a final, opinionated investment verdict on building: **{idea}**

**Go/No-Go Score: X/10**
(1 = definitely don't build, 10 = drop everything and build this)

**Scoring Breakdown:**

| Dimension | Score (1-10) | Rationale |
|-----------|-------------|-----------|
| Market Size | | |
| Problem Severity | | |
| Competitive Landscape | | |
| Timing | | |
| Execution Feasibility | | |
| Monetization Potential | | |

**Bull Case (Why This Wins):**
List 5 specific reasons this succeeds.

**Bear Case (Why This Fails):**
List 5 specific reasons this fails.

**Critical Assumptions:**
5 things that MUST be true for this to work.

**If Go — Next Steps:**
1. [Specific action with owner and timeline]
2.
3.
4.
5.

**Final Verdict:**
2-3 sentences. Be direct and opinionated. No hedging.""",
    ),
]
