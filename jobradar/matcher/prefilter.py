"""Cheap rules pass: is a job even worth scoring/LLM-judging?

Returns (passes, reasons). Used to (a) skip clearly-irrelevant jobs and
(b) feed signal into the heuristic scorer.
"""
from __future__ import annotations

from typing import Tuple

# foreign / offshore tokens -> we only want US/domestic (or remote-US) roles
OFFSHORE = [
    "bulgaria", "bogot", "colombia", "india", "philippines", "romania", "poland",
    "ukraine", "united kingdom", ", uk", "london", "ireland", "dublin", "germany",
    "berlin", "france", "paris", "spain", "portugal", "lisbon", "netherlands",
    "amsterdam", "sweden", "malta", "gibraltar", "australia", "sydney", "melbourne",
    "canada", "toronto", "vancouver", "mexico", "brazil", "singapore", "japan",
    "tokyo", "china", "hong kong", "israel", "tel aviv", "costa rica", "argentina",
]


def _has(text: str, needles) -> bool:
    t = (text or "").lower()
    return any(n in t for n in needles)


def prefilter(title: str, location: str, description: str, profile) -> Tuple[bool, dict]:
    loc = (location or "").lower()
    text = f"{title} {description}".lower()

    is_remote = "remote" in loc or "remote" in text[:400]
    metro_hit = _has(loc, profile.metros)
    # offshore only kills it if it's clearly foreign AND not a US-remote posting
    offshore = _has(loc, OFFSHORE) and not (is_remote and _has(loc, ["us", "u.s", "united states", "america"]))

    kw_hits = [k.strip() for k in profile.keywords if k.strip() and k.strip() in text]
    neg = _has(text, profile.negatives)

    passes = bool(kw_hits) and not offshore
    return passes, {
        "remote": is_remote,
        "metro_hit": metro_hit,
        "offshore": offshore,
        "keyword_hits": kw_hits,
        "negative": neg,
    }
