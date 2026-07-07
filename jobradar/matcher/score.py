"""Score unscored jobs: prefilter -> (Claude judge if keyed, else heuristic) -> save."""
from __future__ import annotations

from .judge import claude_score, heuristic_score
from .prefilter import prefilter
from .profile import load_profile


def score_unscored(settings, store) -> int:
    profile = load_profile(settings)
    use_claude = bool(settings.ANTHROPIC_API_KEY)
    model = settings.ANTHROPIC_MODEL if use_claude else "heuristic"

    scored = 0
    # process the full backlog in batches (safety cap to avoid runaway)
    for _ in range(50):
        jobs = store.fetch_unscored(model=model, limit=300)
        if not jobs:
            break
        _score_batch(jobs, settings, store, profile, model, use_claude)
        scored += len(jobs)
    return scored


def _score_batch(jobs, settings, store, profile, model, use_claude) -> None:
    for j in jobs:
        title, loc, desc = j.get("title", ""), j.get("location", ""), j.get("description", "")
        passes, pf = prefilter(title, loc, desc, profile)

        if not passes:
            # record a low score so we don't re-evaluate every run
            store.save_score(j["id"], {"fit_score": 20, "archetype": "filtered",
                                       "matched_strengths": pf.get("keyword_hits"), "gaps": ["prefilter: off-target"],
                                       "lead_with": None, "rationale": "dropped by prefilter", "model": model})
            continue

        result = None
        if use_claude:
            result = claude_score(settings, profile.prompt_block(), j.get("company", ""), title, loc, desc)
        if result is None:
            result = heuristic_score(title, loc, desc, pf)
            result["model"] = model  # attribute to the active model slot even on heuristic fallback

        store.save_score(j["id"], result)
