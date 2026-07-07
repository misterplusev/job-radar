"""Scoring: a free heuristic judge (always available) and a Claude judge (when keyed)."""
from __future__ import annotations

import json
import re
from typing import Optional

STRONG = ["machine learning", "reinforcement learning", "neural network", "transformer",
          "predictive model", "forecasting", "data scientist", "ml engineer",
          "machine-learning", "deep learning"]
MEDIUM = ["data engineer", "analytics", "quantitative", "research scientist", "data analyst",
          "statistician", "ai ", "research", "trading", "sportsbook", "prediction market"]
LIGHT = ["backend", "software engineer", "operations", "python", "sql"]

ARCHETYPES = [
    ("ML / Data Science", STRONG),
    ("Data / Analytics", ["data engineer", "analytics", "data analyst", "quantitative", "statistician"]),
    ("Trading / Sportsbook / Prediction Markets", ["trading", "sportsbook", "prediction market", "quant"]),
    ("Robotics / Autonomous Ops", ["robot", "autonomous", "fleet", "field operations"]),
    ("Software Engineering", ["software engineer", "backend", "full stack", "platform"]),
]


def _count(text: str, needles) -> int:
    return sum(1 for n in needles if n in text)


def heuristic_score(title: str, location: str, description: str, pf: dict) -> dict:
    text = f"{title} {description}".lower()
    title_l = (title or "").lower()
    score = 45
    score += 20 * min(_count(text, STRONG), 2)   # up to +40
    score += 8 * min(_count(text, MEDIUM), 2)     # up to +16
    score += 3 * min(_count(text, LIGHT), 2)
    # title hits weigh more than body mentions
    if _count(title_l, STRONG):
        score += 8
    if pf.get("metro_hit"):
        score += 15
    elif pf.get("remote"):
        score += 10
    if pf.get("offshore"):
        score -= 45
    if pf.get("negative"):
        score -= 45
    if any(k in text for k in ["sportsbook", "trading", "prediction market", "quant"]):
        score += 6  # ABET/DoorDash synergy
    # seniority realism: he's not a Staff/Principal/Director/VP-level hire (foot-in-door pivot)
    if any(w in title_l for w in ["staff ", "principal", "director", "vp ", "vice president", "head of", "distinguished"]):
        score -= 10
    if "product manager" in title_l and not _count(title_l, STRONG + MEDIUM):
        score -= 12
    score = max(0, min(100, score))

    archetype = "General"
    best = 0
    for name, kws in ARCHETYPES:
        c = _count(text, kws)
        if c > best:
            best, archetype = c, name

    strengths = pf.get("keyword_hits", [])[:6]
    gaps = []
    if "phd" in text and not any(s in ("machine learning", "reinforcement learning") for s in strengths):
        gaps.append("may require PhD")
    if pf.get("offshore"):
        gaps.append("location may be offshore/non-US")

    return {
        "fit_score": score,
        "archetype": archetype,
        "matched_strengths": strengths,
        "gaps": gaps,
        "lead_with": _lead_with(archetype),
        "rationale": f"heuristic: {len(strengths)} matrix-keyword hits; "
                     f"{'metro' if pf.get('metro_hit') else ('remote' if pf.get('remote') else 'location n/a')}.",
        "model": "heuristic",
    }


def _lead_with(archetype: str) -> str:
    return {
        "ML / Data Science": "ABET ML platform + predictive models",
        "Data / Analytics": "ABET data engineering (41M rows) + analytics",
        "Trading / Sportsbook / Prediction Markets": "ABET odds/edge engine + finance background",
        "Robotics / Autonomous Ops": "DoorDash Labs autonomous field ops + Army ops",
        "Software Engineering": "ABET full-stack (Python/Rust/React) build",
    }.get(archetype, "ABET founder + cross-industry breadth")


# --------------------------------------------------------------------------- #
# Claude judge (used only when ANTHROPIC_API_KEY is present)
# --------------------------------------------------------------------------- #
_PROMPT = """You are screening a job posting for a specific candidate. Score fit 0-100.

CANDIDATE PROFILE (the rubric):
{profile}

JOB POSTING:
Company: {company}
Title: {title}
Location: {location}
Description (truncated): {description}

Return ONLY compact JSON with keys:
fit_score (int 0-100), archetype (short string), matched_strengths (array of <=5 short strings),
gaps (array of <=4 short strings), lead_with (one short phrase), rationale (<=2 sentences).
Honor the candidate's guardrails; never invent qualifications. Penalize offshore/non-US, internships, and clearly off-target roles."""


def claude_score(settings, profile_text: str, company: str, title: str, location: str, description: str) -> Optional[dict]:
    try:
        import anthropic
    except Exception:
        return None
    try:
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        msg = client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=500,
            messages=[{"role": "user", "content": _PROMPT.format(
                profile=profile_text[:6000], company=company, title=title,
                location=location or "n/a", description=(description or "")[:4000])}],
        )
        raw = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
        data = json.loads(re.search(r"\{.*\}", raw, re.S).group(0))
        data["model"] = settings.ANTHROPIC_MODEL
        data["fit_score"] = int(data.get("fit_score", 0))
        return data
    except Exception:
        return None
