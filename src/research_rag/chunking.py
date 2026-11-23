import re
import tiktoken
from research_rag.models import Chunk

ENC = tiktoken.get_encoding("o200k_base")

def count_tokens(text: str) -> int:
    return len(ENC.encode(text))

def chunk_text(
    text: str,
    target_tokens: int = 650,
    overlap_tokens: int = 100,
) -> list[Chunk]:
    paragraphs = [
        re.sub(r"\s+", " ", p).strip()
        for p in re.split(r"\n{2,}", text)
        if p.strip()
    ]
    result: list[Chunk] = []
    current: list[str] = []

    for paragraph in paragraphs:
        candidate = "\n\n".join(current + [paragraph])
        if current and count_tokens(candidate) > target_tokens:
            value = "\n\n".join(current)
            result.append(Chunk(len(result), value, count_tokens(value)))

            overlap: list[str] = []
            total = 0
            for prior in reversed(current):
                n = count_tokens(prior)
                if overlap and total + n > overlap_tokens:
                    break
                overlap.insert(0, prior)
                total += n
            current = overlap + [paragraph]
        else:
            current.append(paragraph)

    if current:
        value = "\n\n".join(current)
        result.append(Chunk(len(result), value, count_tokens(value)))

    return result
