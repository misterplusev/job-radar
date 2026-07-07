"""Generate a tailored resume + cover letter for a specific job.

Claude does the real tailoring when ANTHROPIC_API_KEY is set. Without a key, we assemble
a structured DRAFT from the matrix so there's always something to start from. Every output
is written to GENERATED_DOCS_DIR and an `applications` row (status=draft) is created.

Guardrails come from a private file (CANDIDATE_GUARDRAILS_PATH) and are enforced in the Claude prompt
and noted in the heuristic draft. No fabricated qualifications, ever.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

from ..matcher.profile import load_profile

def _load_guardrails() -> str:
    """Guardrails specific to the candidate come from a private file, never from this repository.

    CANDIDATE_GUARDRAILS_PATH names the file. Without it the sample in config/candidate_guardrails.md is used.
    """
    path = os.environ.get("CANDIDATE_GUARDRAILS_PATH") or str(Path(__file__).resolve().parents[2] / "config" / "candidate_guardrails.md")
    try:
        return Path(path).read_text(encoding="utf-8").strip()
    except OSError:
        return "GUARDRAILS (must obey): Never fabricate any metric, title, or qualification not supported by the profile."


GUARDRAILS = _load_guardrails()
CANDIDATE_NAME = os.environ.get("CANDIDATE_NAME", "Candidate")


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
    resume = header + f"# {CANDIDATE_NAME} — Resume (tailored draft)\n\n" + profile.text
    cover = (header + f"# Cover Letter — {job['company']}\n\n"
             f"Dear Hiring Team,\n\nI'm applying for the {job['title']} role. "
             "My background fits this role in these ways: "
             "[assemble specifics from the matrix relevant to this posting]. "
             f"\n\nSincerely,\n{CANDIDATE_NAME}\n")
    return resume, cover
