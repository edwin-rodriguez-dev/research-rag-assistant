import json
from pathlib import Path

DOCS = {
    "alpha_liquidity_review": {
        "title": "Alpha Fund Liquidity Review",
        "classification": "INTERNAL",
        "allowed_roles": ["RESEARCH", "PM", "ADMIN"],
        "text": """Alpha Fund Liquidity Review

Executive Summary
Alpha Fund maintains concentrated large-cap technology exposure.

Key Liquidity Risk
The most important liquidity concern is crowded technology positioning combined with reduced dealer balance-sheet capacity during a broad volatility event. Under the stress scenario, the estimated liquidation horizon rises from two trading days to six trading days.

Mitigation
The portfolio manager agreed to retain a larger Treasury-bill buffer and reduce two less-liquid technology positions.
""",
    },
    "beta_energy_memo": {
        "title": "Beta Fund Energy Strategy Memo",
        "classification": "INTERNAL",
        "allowed_roles": ["RESEARCH", "PM", "ADMIN"],
        "text": """Beta Fund Energy Strategy Memo

Beta Fund has a deliberate overweight to integrated oil producers and oil-field services companies. The largest scenario risk is a rapid decline in crude oil below 55 dollars per barrel. A sustained move below that level could reduce expected twelve-month return by approximately five percentage points. The team uses selective put spreads on an energy-sector ETF.
""",
    },
    "gamma_restricted_acquisition": {
        "title": "Gamma Restricted Acquisition Analysis",
        "classification": "RESTRICTED",
        "allowed_roles": ["PM", "ADMIN"],
        "text": """Gamma Restricted Acquisition Analysis

This document is restricted to portfolio managers and administrators. Gamma Fund is evaluating a hypothetical acquisition-related position in Northstar Components. The internal working assumption is a 38 dollar offer price. The principal risk is deal failure following regulatory review. No trade may be initiated solely from this document.
""",
    },
    "delta_ai_infrastructure": {
        "title": "Delta Technology AI Infrastructure Outlook",
        "classification": "INTERNAL",
        "allowed_roles": ["RESEARCH", "PM", "ADMIN"],
        "text": """Delta Technology AI Infrastructure Outlook

The team expects hyperscaler capital expenditures to remain elevated because of accelerated computing, networking, and data-center power infrastructure. Power availability is viewed as the most important physical constraint on new AI data-center capacity over the next twenty-four months. Transformer lead times and grid interconnection queues are secondary constraints.
""",
    },
    "epsilon_public_strategy": {
        "title": "Epsilon Strategy Overview",
        "classification": "PUBLIC",
        "allowed_roles": ["PUBLIC", "RESEARCH", "PM", "ADMIN"],
        "text": """Epsilon Strategy Overview

Epsilon is a diversified long-short equity strategy emphasizing fundamental security selection, position sizing, and disciplined risk management. This overview is public and contains no confidential positions or forecasts.
""",
    },
    "research_governance_policy": {
        "title": "Research Information Governance Policy",
        "classification": "INTERNAL",
        "allowed_roles": ["RESEARCH", "PM", "ADMIN"],
        "text": """Research Information Governance Policy

Documents are classified as PUBLIC, INTERNAL, or RESTRICTED. PUBLIC material may be retrieved by any user. INTERNAL research may be retrieved by RESEARCH or PM roles. RESTRICTED material may be retrieved only by PM or ADMIN. Authorization must be applied before document chunks are supplied to a language model; prompt instructions alone are not an access-control mechanism. Audit records must retain the user, role, question, retrieved chunks and documents, model, and elapsed time.
""",
    },
}

if __name__ == "__main__":
    output = Path("data/raw/synthetic")
    output.mkdir(parents=True, exist_ok=True)

    for slug, document in DOCS.items():
        (output / f"{slug}.txt").write_text(
            document["text"].strip() + "\n",
            encoding="utf-8",
        )
        (output / f"{slug}.json").write_text(
            json.dumps(
                {
                    "external_id": f"synthetic:{slug}",
                    "title": document["title"],
                    "company": None,
                    "document_type": "INTERNAL_RESEARCH",
                    "source_type": "SYNTHETIC",
                    "source_url": None,
                    "filing_date": None,
                    "classification": document["classification"],
                    "allowed_roles": document["allowed_roles"],
                    "synthetic": True,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"Created {slug}")
