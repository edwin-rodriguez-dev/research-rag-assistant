import argparse
from research_rag.governance import normalize_role
from research_rag.retrieval import HybridRetriever

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("question")
    parser.add_argument("--role", default="PUBLIC")
    args = parser.parse_args()

    results = HybridRetriever().search(
        args.question,
        normalize_role(args.role),
    )

    for index, result in enumerate(results, start=1):
        print("\n" + "=" * 70)
        print(
            f"{index}. {result.title} "
            f"score={result.score:.5f} "
            f"vector={result.vector_rank} "
            f"keyword={result.keyword_rank}"
        )
        print(
            f"classification={result.classification} "
            f"chunk={result.chunk_number}"
        )
        print(result.text[:1500])
