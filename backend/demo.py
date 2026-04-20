"""Demo / mock pipeline — simulates the full agent flow without any API keys."""

from __future__ import annotations

import asyncio
import json
from typing import AsyncGenerator

DEMO_QUERY = None  # filled dynamically

# ── Simulated outputs ────────────────────────────────────────

_RESEARCH_PLAN = """\
## Research Plan

Based on the query, I have identified the following sub-questions:

1. **Current Interest Rate Landscape (2026)** — What are the latest Federal Reserve rate decisions and forward guidance for 2026?
2. **Renewable Energy Sector Fundamentals** — What is the current state of solar, wind, and battery storage markets in terms of capacity, investment, and policy support?
3. **Interest Rate Impact on Capital-Intensive Industries** — How do rising rates affect project financing costs, IRR thresholds, and investment decisions in renewables?
4. **Historical Precedent Analysis** — During previous rate hike cycles (2017-2018, 2022-2023), how did renewable energy stocks and project pipelines respond?
5. **Policy & Subsidy Interactions** — How do IRA (Inflation Reduction Act) tax credits interact with higher borrowing costs to affect net project economics?
"""

_RESEARCH_BRIEF = """\
## Research Brief

### 1. Current Interest Rate Landscape

The Federal Reserve raised the federal funds rate to 5.75-6.00% in Q1 2026, marking the highest level since 2001.
- [Reuters](https://reuters.com): "Fed holds rates steady amid persistent core inflation at 3.2%"
- [Bloomberg](https://bloomberg.com): "Markets price in two additional 25bp hikes by mid-2026"

### 2. Renewable Energy Sector Fundamentals

Global renewable energy investment reached $1.1 trillion in 2025, with solar accounting for 60%.
- [IRENA](https://irena.org): "Solar PV costs declined 8% in 2025 to $0.032/kWh global average"
- [BloombergNEF](https://about.bnef.com): "Battery storage deployments grew 45% YoY in 2025"

### 3. Impact on Capital-Intensive Industries

Higher interest rates increase the weighted average cost of capital (WACC) for renewable projects by 150-200 basis points.
- [McKinsey Energy Insights](https://mckinsey.com): "Every 100bp increase in WACC reduces solar project IRR by 1.2-1.5 percentage points"
- [Lazard LCOE Analysis](https://lazard.com): "Levelized cost of wind increased 12% in high-rate environments"

### 4. Historical Precedent

During the 2022-2023 rate hike cycle, the S&P Clean Energy Index declined 28% while project pipelines contracted 15%.
- [S&P Global](https://spglobal.com): "Renewable project delays doubled during 2022-2023 tightening cycle"
- [Wood Mackenzie](https://woodmac.com): "US solar installations fell 16% in H2 2023 due to financing headwinds"

### 5. Policy & Subsidy Interactions

IRA tax credits (30% ITC, $26/MWh PTC) offset approximately 60-70% of the rate-driven cost increase.
- [DOE](https://energy.gov): "IRA credits expected to support 150 GW of new clean energy by 2030"
- [Tax Foundation](https://taxfoundation.org): "Transferable tax credits market reached $12B in 2025"
"""


def _build_draft(query: str) -> str:
    return f"""\
# Impact of 2026 Interest Rate Hikes on the Renewable Energy Sector

## Executive Summary

The Federal Reserve's aggressive monetary tightening in 2026, with rates reaching 5.75-6.00%, presents a **significant but nuanced challenge** for the renewable energy sector. While higher borrowing costs increase project WACC by 150-200 basis points and reduce unsubsidized IRRs by 1.2-1.5 percentage points, the Inflation Reduction Act's robust tax credit framework offsets 60-70% of this impact. This whitepaper analyzes the multi-dimensional effects across project economics, capital markets, and long-term sector trajectories.

## 1. The Macroeconomic Context

The Federal Reserve's decision to raise the federal funds rate to 5.75-6.00% in Q1 2026 represents the most restrictive monetary policy in over two decades ([Reuters](https://reuters.com)). Core inflation remains sticky at 3.2%, with markets pricing in two additional 25bp hikes by mid-2026 ([Bloomberg](https://bloomberg.com)).

For the renewable energy sector — inherently capital-intensive with high upfront costs and long payback periods — this environment creates material headwinds for project financing.

## 2. Direct Impact on Project Economics

### 2.1 Cost of Capital

Rising rates directly increase the Weighted Average Cost of Capital (WACC) for renewable energy projects:

| Metric | Low-Rate Env (2021) | Current (2026) | Delta |
|:---|:---|:---|:---|
| Project WACC | 5.5% | 7.5% | +200 bps |
| Solar IRR (unsubsidized) | 12.1% | 10.6% | -1.5 pp |
| Wind IRR (unsubsidized) | 10.8% | 9.5% | -1.3 pp |
| Levelized Cost of Solar | $0.028/kWh | $0.035/kWh | +25% |

*Source: [McKinsey Energy Insights](https://mckinsey.com), [Lazard LCOE Analysis](https://lazard.com)*

### 2.2 Project Pipeline Impact

Historical precedent suggests significant pipeline contraction. During the 2022-2023 rate hike cycle, the S&P Clean Energy Index declined 28% and US solar installations fell 16% in H2 2023 ([S&P Global](https://spglobal.com), [Wood Mackenzie](https://woodmac.com)). Project delays doubled as developers struggled to secure financing at acceptable rates.

## 3. The IRA Shield Effect

The Inflation Reduction Act provides a critical buffer through its tax credit framework:

- **30% Investment Tax Credit (ITC)** for solar and storage projects
- **$26/MWh Production Tax Credit (PTC)** for wind projects
- **Transferable tax credits** market reached $12B in 2025 ([Tax Foundation](https://taxfoundation.org))

These credits offset approximately **60-70% of the rate-driven cost increase**, effectively reducing the net WACC impact from 200 bps to approximately 60-80 bps ([DOE](https://energy.gov)).

## 4. Sector-Specific Analysis

### Solar
Solar remains the most resilient sub-sector due to continued cost declines (-8% in 2025) and strong ITC support. However, utility-scale projects face greater financing pressure than distributed/rooftop installations ([IRENA](https://irena.org)).

### Wind
Onshore wind faces the steepest headwinds due to higher capital intensity and longer development timelines. Offshore wind projects with 7-10 year development cycles are particularly vulnerable to sustained high rates.

### Battery Storage
Battery storage deployments grew 45% YoY in 2025 ([BloombergNEF](https://about.bnef.com)) and are **partially insulated** from rate impacts due to strong revenue visibility from grid services contracts.

## 5. Investment Outlook & Recommendations

| Scenario | Probability | Sector Impact |
|:---|:---|:---|
| Rates peak Q2 2026, cuts begin Q4 | 40% | Moderate recovery, 15-20% pipeline rebound |
| Rates plateau through 2026 | 35% | Continued pressure, 5-10% further contraction |
| Rates rise above 6.25% | 25% | Severe stress, 20-30% pipeline reduction |

### Key Recommendations for Investors:

1. **Favor distributed solar** over utility-scale in high-rate environments
2. **Battery storage** offers the best risk-adjusted returns due to revenue certainty
3. **Monitor IRA implementation** — any political risk to tax credits would compound rate pressure
4. **Consider tax credit transfer markets** as an alternative financing mechanism

## 6. Conclusion

The 2026 interest rate environment creates a **two-speed renewable energy market**: projects with IRA tax credit eligibility and strong PPA contracts remain economically viable, while unsubsidized or early-stage projects face significant financing headwinds. The sector's long-term trajectory remains positive, but near-term capital allocation decisions require careful analysis of project-level economics under sustained high-rate assumptions.

---

*Report generated by the Multi-Agent AI Research Team — Powered by Claude 3.5 Sonnet*
"""


_FACT_CHECK_PASS = {
    "verdict": "APPROVED",
    "overall_confidence": 87,
    "claims": [
        {"claim": "Fed raised rates to 5.75-6.00%", "confidence": 92, "issue": None},
        {"claim": "Core inflation at 3.2%", "confidence": 88, "issue": None},
        {"claim": "Global renewable investment $1.1T", "confidence": 85, "issue": None},
        {"claim": "Solar costs declined 8% in 2025", "confidence": 90, "issue": None},
        {"claim": "WACC increase of 150-200 bps", "confidence": 82, "issue": None},
        {"claim": "IRA credits offset 60-70% of cost increase", "confidence": 78, "issue": None},
        {"claim": "S&P Clean Energy Index declined 28%", "confidence": 91, "issue": None},
        {"claim": "Battery storage grew 45% YoY", "confidence": 86, "issue": None},
    ],
    "summary": "The report is well-sourced with inline citations for all major claims. Overall confidence is high at 87%. All individual claims score above the 70% threshold.",
}

_FACT_CHECK_FAIL = {
    "verdict": "NEEDS_REVISION",
    "overall_confidence": 64,
    "claims": [
        {"claim": "Fed raised rates to 5.75-6.00%", "confidence": 92, "issue": None},
        {"claim": "Solar costs declined 8% in 2025", "confidence": 90, "issue": None},
        {"claim": "WACC increase of 150-200 bps", "confidence": 58, "issue": "McKinsey source is from 2024; needs a 2026 update or caveat."},
        {"claim": "IRA credits offset 60-70% of cost increase", "confidence": 52, "issue": "Percentage range not directly supported by cited DOE source."},
        {"claim": "Battery storage grew 45% YoY", "confidence": 86, "issue": None},
    ],
    "summary": "Two claims scored below the 70% confidence threshold. The WACC impact range and IRA offset percentage need stronger sourcing or caveats.",
}


# ── Async SSE generator ─────────────────────────────────────

def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


async def demo_sse_stream(query: str) -> AsyncGenerator[str, None]:
    """Simulate the full 4-agent pipeline with realistic delays."""

    yield _sse("status", {"message": "🚀 Starting multi-agent research pipeline (DEMO MODE)..."})
    await asyncio.sleep(1.0)

    # ── Supervisor ───────────────────────────────────────────
    yield _sse("agent_log", {
        "agent": "supervisor",
        "message": "🧑‍💼 **Supervisor** — Analyzing query and decomposing into research sub-questions..."
    })
    await asyncio.sleep(2.5)

    yield _sse("agent_log", {
        "agent": "supervisor",
        "message": "🧑‍💼 **Supervisor** — Received query and created research plan."
    })
    await asyncio.sleep(1.0)

    # ── Researcher ───────────────────────────────────────────
    yield _sse("agent_log", {
        "agent": "researcher",
        "message": "🕵️ **Researcher** — Launching web searches for 5 sub-topics..."
    })
    await asyncio.sleep(2.0)

    for i, topic in enumerate([
        "2026 Federal Reserve interest rate decisions",
        "renewable energy sector market analysis 2026",
        "interest rate impact on capital intensive industries",
        "historical rate hike impact on clean energy stocks",
        "IRA tax credits interaction with borrowing costs",
    ], 1):
        yield _sse("agent_log", {
            "agent": "researcher",
            "message": f"🕵️ **Researcher** — Searching [{i}/5]: *{topic}*..."
        })
        await asyncio.sleep(1.5)

    yield _sse("agent_log", {
        "agent": "researcher",
        "message": "🕵️ **Researcher** — Searched 5 sub-topics and compiled a Research Brief."
    })
    await asyncio.sleep(1.0)

    # ── Writer (first draft) ─────────────────────────────────
    yield _sse("agent_log", {
        "agent": "writer",
        "message": "✍️ **Writer** — Drafting initial report with citations..."
    })
    await asyncio.sleep(3.0)

    yield _sse("agent_log", {
        "agent": "writer",
        "message": "✍️ **Writer** — Drafted the report (revision #0)."
    })
    await asyncio.sleep(1.0)

    # ── Fact-Checker (FAIL → revision loop) ──────────────────
    yield _sse("agent_log", {
        "agent": "fact_checker",
        "message": "🔍 **Fact-Checker** — Reviewing draft against research sources..."
    })
    await asyncio.sleep(2.5)

    yield _sse("agent_log", {
        "agent": "fact_checker",
        "message": "🔍 **Fact-Checker** — 🔄 Overall confidence: 64%. Requesting revision."
    })
    await asyncio.sleep(1.0)

    yield _sse("agent_log", {
        "agent": "fact_checker",
        "message": "🔍 **Fact-Checker** — ⚠️ Issues: WACC source outdated; IRA offset % needs stronger citation."
    })
    await asyncio.sleep(1.5)

    # ── Writer (revision) ────────────────────────────────────
    yield _sse("agent_log", {
        "agent": "writer",
        "message": "✍️ **Writer** — Addressing fact-check feedback and revising..."
    })
    await asyncio.sleep(2.5)

    yield _sse("agent_log", {
        "agent": "writer",
        "message": "✍️ **Writer** — Revised the report (revision #1)."
    })
    await asyncio.sleep(1.0)

    # ── Fact-Checker (PASS) ──────────────────────────────────
    yield _sse("agent_log", {
        "agent": "fact_checker",
        "message": "🔍 **Fact-Checker** — Re-reviewing revised draft..."
    })
    await asyncio.sleep(2.0)

    yield _sse("agent_log", {
        "agent": "fact_checker",
        "message": "🔍 **Fact-Checker** — ✅ Overall confidence: 87%. Approved!"
    })
    await asyncio.sleep(0.5)

    # ── Final report ─────────────────────────────────────────
    yield _sse("final_report", {"report": _build_draft(query)})
    yield _sse("done", {"message": "✅ Research pipeline complete (DEMO MODE)."})
