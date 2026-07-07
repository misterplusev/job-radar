"""Load the candidate profile from the skills matrix markdown."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

_FALLBACK = "Sample candidate (made-up): operations and data background, Python and SQL, targets robotics operations and data roles, remote US. Never fabricate."


@dataclass
class CandidateProfile:
    text: str
    metros: List[str]
    keywords: List[str]
    negatives: List[str]

    def prompt_block(self, limit: int = 7000) -> str:
        return self.text[:limit]


def load_profile(settings) -> CandidateProfile:
    text = _FALLBACK
    p = Path(settings.MATRIX_PATH)
    try:
        if p.exists():
            text = p.read_text(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    return CandidateProfile(text=text, metros=settings.TARGET_METROS,
                            keywords=settings.TARGET_KEYWORDS, negatives=settings.NEGATIVE_KEYWORDS)
