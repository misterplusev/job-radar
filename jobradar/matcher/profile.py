"""Load the candidate profile from the skills matrix markdown."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

_FALLBACK = """Christopher Layman — target: machine learning, reinforcement learning,
neural networks/transformers, predictive modeling, data science/engineering, quantitative,
sportsbook/trading operations. Breadth: Army officer (leadership/ops), Morgan Stanley &
Columbia Bank (finance/compliance), real estate, ABET sports-analytics founder (Python, SQL,
PostgreSQL 41M rows, LightGBM/XGBoost, Cloudflare/HF/Supabase), DoorDash Labs autonomous
robotics field ops. Locations: Phoenix, Seattle, SF/Bay, San Diego, Denver, or remote.
Comp target: meaningful step up from ~$26/hr. Guardrails: Columbia Bank=Seattle not Tacoma;
never claim the Umpqua merger; Series 7/63 lapsed (previously held); never fabricate."""


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
