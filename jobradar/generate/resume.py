"""Generate a tailored resume + cover letter for a specific job.

Claude does the real tailoring when ANTHROPIC_API_KEY is set. Without a key, we assemble
a structured DRAFT from the matrix so there's always something to start from. Every output
is written to GENERATED_DOCS_DIR and an `applications` row (status=draft) is created.

Guardrails (enforced in the Claude prompt and noted in the heuristic draft):
  - Columbia Bank = Seattle, WA (not Tacoma)
  - Never claim the Umpqua (~$5B) merger — left before it
  - Series 7/63 = "previously held" (lapsed), never "active"
  - No fabricated qualifications, ever
"""
from __future__ import annotations

import re
from pathlib import Path

from ..matcher.profile import load_profile

GUARDRAILS = (
    "GUARDRAILS (must obey): Columbia Bank location is Seattle, WA (never Tacoma). "
    "Never claim participation in the Umpqua (~$5B) acquisition — he left before it. "
    "FINRA Series 7 & 63 are lapsed — say 'previously held', never 'active'. "
    "Never fabricate any metric, title, or qualification not supported by the profile."
)


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", (s or "").lower()).strip("_")[:40]


def generate_for_job(settings, store, job_id: int) -> dict:
    job = store.get_job(job_id)
    if not job:
        raise SystemExit(f"job {job_id} not found")
    profile = load_profile(settings)
    outdir = Path(settings.GENERATED_DOCS_DIR)
    outdir.mkdir(parents=True, exist_ok=True)
    stem = f"{_slug(job['company'])}__{_slug(job['title'])}"

    if settings.ANTHROPIC_API_KEY:
        resume_md, cover_md = _claude_docs(settings, profile.prompt_block(), job)
    else:
        resume_md, cover_md = _heuristic_docs(profile, job)

    resume_path = outdir / f"{stem}__RESUME.md"
    cover_path = outdir / f"{stem}__COVER.md"
    resume_path.write_text(resume_md, encoding="utf-8")
    cover_path.write_text(cover_md, encoding="utf-8")

    store.upsert_application({
        "company": job["company"], "job_url": job["url"], "job_title": job["title"],
        "status": "draft", "resume_path": str(resume_path), "cover_path": str(cover_path),
        "notes": "auto-generated draft — review before submitting",
    })
    return {"resume": str(resume_path), "cover": str(cover_path)}


def _claude_docs(settings, profile_text: str, job: dict):
    import anthropic
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    prompt = (
        f"{GUARDRAILS}\n\nCANDIDATE PROFILE / SKILLS MATRIX:\n{profile_text}\n\n"
        f"JOB:\nCompany: {job['company']}\nTitle: {job['title']}\n"
        f"Location: {job.get('location')}\nDescription:\n{(job.get('description') or '')[:5000]}\n\n"
        "Write two documents in Markdown, separated by a line '===COVER==='. "
        "First a one-page tailored RESUME, then a one-page COVER LETTER. "
        "Lead with the experience most relevant to this job per the matrix. Truthful, specific, no fabrication."
    )
    msg = client.messages.create(model=settings.ANTHROPIC_MODEL, max_tokens=2500,
                                 messages=[{"role": "user", "content": prompt}])
    raw = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    parts = raw.split("===COVER===")
    resume = parts[0].strip()
    cover = (parts[1].strip() if len(parts) > 1 else "")
    return resume, cover


def _heuristic_docs(profile, job: dict):
    header = (f"> DRAFT (assembled from matrix — refine with the Claude judge/generator).\n"
              f"> Target: {job['title']} @ {job['company']} ({job.get('location')})\n"
              f"> {GUARDRAILS}\n\n")
    resume = header + "# Christopher Layman — Resume (tailored draft)\n\n" + profile.text
    cover = (header + f"# Cover Letter — {job['company']}\n\n"
             f"Dear Hiring Team,\n\nI'm applying for the {job['title']} role. "
             "My background spans ML/predictive analytics (ABET), finance, and operations leadership "
             "[assemble specifics from the matrix relevant to this posting]. "
             "\n\nSincerely,\nChristopher Layman\n")
    return resume, cover
