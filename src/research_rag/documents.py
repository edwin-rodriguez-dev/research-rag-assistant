import hashlib
import json
import re
import time
from pathlib import Path
from datetime import date

import requests
from bs4 import BeautifulSoup

from research_rag.config import settings, required
from research_rag.models import SourceDocument

SEC_DATA = "https://data.sec.gov"
SEC_WWW = "https://www.sec.gov"
SEC_ARCHIVES = "https://www.sec.gov/Archives/edgar/data"
DELAY_SECONDS = 0.15

def sec_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": required(settings().sec_user_agent, "SEC_USER_AGENT"),
            "Accept-Encoding": "gzip, deflate",
        }
    )
    return session

def _get_json(session: requests.Session, url: str) -> dict:
    response = session.get(url, timeout=30)
    response.raise_for_status()
    time.sleep(DELAY_SECONDS)
    return response.json()

def _get_text(session: requests.Session, url: str) -> str:
    response = session.get(url, timeout=60)
    response.raise_for_status()
    time.sleep(DELAY_SECONDS)
    return response.text

def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    lines = [
        re.sub(r"\s+", " ", value).strip()
        for value in soup.get_text("\n").splitlines()
        if value.strip()
    ]
    return "\n\n".join(lines)

def fetch_sec(
    tickers: list[str],
    forms: list[str],
    per_form: int,
    output_dir: Path,
) -> int:
    session = sec_session()
    output_dir.mkdir(parents=True, exist_ok=True)
    ticker_data = _get_json(session, f"{SEC_WWW}/files/company_tickers.json")
    ticker_map = {
        value["ticker"].upper(): int(value["cik_str"])
        for value in ticker_data.values()
    }

    count = 0
    for ticker in tickers:
        ticker = ticker.upper()
        cik = ticker_map[ticker]
        submissions = _get_json(
            session,
            f"{SEC_DATA}/submissions/CIK{cik:010d}.json",
        )
        recent = submissions["filings"]["recent"]

        for form in forms:
            found = 0
            for index, value in enumerate(recent["form"]):
                if value != form:
                    continue

                accession = recent["accessionNumber"][index]
                primary = recent["primaryDocument"][index]
                filed = recent["filingDate"][index]
                url = (
                    f"{SEC_ARCHIVES}/{cik}/"
                    f"{accession.replace('-', '')}/{primary}"
                )
                text = html_to_text(_get_text(session, url))
                slug = f"{ticker}_{form.replace('-', '')}_{filed}"

                (output_dir / f"{slug}.txt").write_text(
                    text,
                    encoding="utf-8",
                )
                (output_dir / f"{slug}.json").write_text(
                    json.dumps(
                        {
                            "external_id": accession,
                            "title": (
                                f"{submissions.get('name', ticker)} "
                                f"{form} filed {filed}"
                            ),
                            "company": submissions.get("name", ticker),
                            "document_type": form,
                            "source_type": "SEC",
                            "source_url": url,
                            "filing_date": filed,
                            "classification": "PUBLIC",
                            "allowed_roles": [
                                "PUBLIC",
                                "RESEARCH",
                                "PM",
                                "ADMIN",
                            ],
                        },
                        indent=2,
                    ),
                    encoding="utf-8",
                )
                found += 1
                count += 1
                if found >= per_form:
                    break

    return count

def discover_documents() -> list[Path]:
    result: list[Path] = []
    for root in (Path("data/raw/sec"), Path("data/raw/synthetic")):
        if root.exists():
            result.extend(sorted(root.glob("*.txt")))
    return result

def load_document(path: Path) -> tuple[SourceDocument, str]:
    text = path.read_text(encoding="utf-8")
    metadata = json.loads(
        path.with_suffix(".json").read_text(encoding="utf-8")
    )
    filed = (
        date.fromisoformat(metadata["filing_date"])
        if metadata.get("filing_date")
        else None
    )

    return (
        SourceDocument(
            external_id=metadata["external_id"],
            title=metadata["title"],
            company=metadata.get("company"),
            document_type=metadata["document_type"],
            source_type=metadata["source_type"],
            source_url=metadata.get("source_url"),
            filing_date=filed,
            classification=metadata.get("classification", "PUBLIC"),
            local_path=path,
            checksum=hashlib.sha256(text.encode()).hexdigest(),
            allowed_roles=metadata.get("allowed_roles", ["PUBLIC"]),
            metadata=metadata,
        ),
        text,
    )
