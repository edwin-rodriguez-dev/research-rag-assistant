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
