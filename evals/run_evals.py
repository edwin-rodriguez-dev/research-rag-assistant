from research_rag.rag import RAGService

CASES = [
    (
        "Alpha liquidity",
        "What is Alpha Fund's main liquidity risk?",
        "RESEARCH",
        "Alpha Fund Liquidity Review",
        None,
        ("technology", "dealer", "six"),
    ),
    (
        "Beta energy",
        "What oil-price scenario is the biggest risk for Beta?",
        "RESEARCH",
        "Beta Fund Energy Strategy Memo",
        None,
        ("55", "oil"),
    ),
    (
        "Restricted blocked",
        "What offer price is Gamma evaluating?",
        "RESEARCH",
        None,
        "Gamma Restricted Acquisition Analysis",
        (),
    ),
    (
        "Restricted allowed",
        "What offer price is Gamma evaluating?",
        "PM",
        "Gamma Restricted Acquisition Analysis",
        None,
        ("38",),
    ),
    (
        "NVIDIA foundries",
        "Which foundries does NVIDIA partner with to manufacture its semiconductor wafers?",
        "PUBLIC",
        "NVIDIA CORP 10-K filed 2026-02-25",
        None,
        ("tsmc", "samsung"),
    ),
    (
        "Goldman liquidity principles",
        "What are the three principles Goldman Sachs uses to manage liquidity risk?",
        "PUBLIC",
        "GOLDMAN SACHS GROUP INC 10-K filed 2026-02-25",
        None,
        ("gcla", "contingency funding"),
    ),
    (
        "Apple AI data center constraints",
        "What external factors or operational constraints affect Apple's ability to build and expand data centers for AI compute capacity?",
        "PUBLIC",
        "Apple Inc. 10-K filed 2026-11-03",
        None,
        ("power", "water"),
    ),
]

if __name__ == "__main__":
    service = RAGService()
    passed = 0

    for name, question, role, expected, forbidden, terms in CASES:
        result = service.answer(
            question,
            "eval-runner",
            role,
        )
        titles = [source["title"] for source in result["sources"]]
        answer = result["answer"].lower()

        ok = (
            (
                expected is None
                or any(expected in title for title in titles)
            )
            and (
                forbidden is None
                or all(forbidden not in title for title in titles)
            )
            and all(term.lower() in answer for term in terms)
        )

        passed += int(ok)
        print(
            f"{name}: {'PASS' if ok else 'FAIL'} | {titles}"
        )

    print(f"Passed {passed}/{len(CASES)}")
    if passed != len(CASES):
        raise SystemExit(1)
