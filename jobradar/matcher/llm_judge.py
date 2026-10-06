"""LLM judge chain v2 — OpenRouter :free (multi-key, rotating) -> NVIDIA NIM -> None.

Never raises. Output contract identical to claude_score/heuristic_score.
Keys from env (documented in E:\\abet\\.env): OPENROUTER_SWARM_API_KEY /
OPENROUTER_HERMES_API_KEY / OPENROUTER_API_KEY, NVIDIA_API_KEY.
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.request

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

FREE_MODELS = [
    "nvidia/nemotron-3-super-120b-a12b:free",
    "google/gemma-4-31b-it:free",
    "thinkingmachines/inkling:free",
    "z-ai/glm-5.2:free",
]
NV_MODEL = "nvidia/nemotron-3-ultra-550b-a55b"

_FACTS = """VERIFIED CANDIDATE FACTS:
MANAGEMENT & LEADERSHIP EXPERIENCE: YES - commissioned officer, US Army Captain:
commanded a 135-person mechanized infantry company (hiring/training/discipline/schedules),
100% accountability for $75MM of equipment, ran safety and maintenance programs,
coordinated multi-unit logistics movements, Ranger School graduate. Plus 4 years
financial-services client/operations work (Morgan Stanley FA; Columbia Bank private
banking, $60MM portfolio across 3 branches).
TECHNICAL/OPERATIONS EXPERIENCE: DoorDash Labs robot field operator (Mar 2026-present):
live autonomous fleet ops - dispatch, bot rescue, telemetry, CV/LiDAR monitoring,
Jenkins/GitHub CI, JIRA. Founder ABET sports analytics since 2022: 41M-row Postgres,
Python/Rust pipelines, LightGBM/XGBoost models, odds ingestion from 18+ sportsbooks.
HARD LIMITS (do not paper over): B.A. Economics only (no graduate degree); zero years
of professional AI/ML employment; has NOT managed industry software-engineering or
research teams; has not managed technical budgets in a corporate setting; ~6 months
paid robotics tenure.
Credential precision: Morgan Stanley role was FINANCIAL ADVISOR (wealth management) - NOT investment banking, NOT private equity, NOT management consulting. No MBA, no master's degree.
Geos: Phoenix AZ, Seattle, SF Bay, Monterey/San Diego CA, Denver, Las Vegas, Remote-US."""

_GATE_PROMPT = """You are a brutal resume screener. Compare the JOB's REQUIRED qualifications against the CANDIDATE FACTS below. For each REQUIRED qualification output met=true ONLY if the facts clearly satisfy it. Degree requirements and minimum-years-of-experience are STRICT - partial or adjacent experience does NOT count. EXCEPTION: requirements for general leadership, team management, operations management, P&L/budget-adjacent accountability, or 'managed teams' ARE satisfied by the candidate's documented Army command (135 personnel, $75MM accountability) plus operations roles - do not FAIL those. Only FAIL them if the requirement explicitly demands managing software engineers, researchers, or corporate technical staff.

FULL JOB POSTING (locate the REQUIRED QUALIFICATIONS / minimum qualifications):
{requirements}

CANDIDATE FACTS:
{facts}

Rules: items under "Required"/"Minimum qualifications" are HARD GATES. Items under "Preferred"/"Nice to have" are NOT gates - ignore them for the verdict entirely.
Return ONLY compact JSON: {{"verdict": "PASS" or "FAIL", "unmet": [short list of failed requirement names], "notes": "<=1 sentence"}}"""

_SCORE_PROMPT = """You are screening a job posting for a specific candidate. Score fit 0-100 with strict calibration: 90+ = meets essentially every stated requirement; 75-89 = solid match with minor gaps; 55-74 = plausible stretch; below 40 = poor. NEVER award 85+ when the posting requires credentials the candidate lacks (graduate degree, N years in a specific discipline, professional licenses). A role seniority far above the candidate's level caps the score at 45. UNMET Preferred qualifications each cost 6-12 points (preferences are never gates, always discounts). When a posting prefers consulting/private-equity/investment-banking/hyper-growth-tech backgrounds, remember the candidate has NONE of those four - only adjacent wealth-management finance and self-founded startup years. For OPERATIONS/field/fleet/logistics management and supervisor roles: the candidate's Army command (135 soldiers, $75MM accountability) and DoorDash Labs shift operations are REAL management experience - score those roles normally rather than capping. Only cap for roles that specifically require managing software engineers or research teams in industry.

CANDIDATE FACTS:
{facts}

JOB:
Company: {company}
Title: {title}
Location: {location}
Description: {description}

Return ONLY compact JSON: {{"fit_score": int, "archetype": "short", "matched_strengths": [<=4], "gaps": [<=3], "lead_with": "short phrase", "rationale": "<=2 sentences"}}"""


def _chat(url, key, model, prompt, max_tokens=3000):
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.2,
    }).encode()
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    req = urllib.request.Request(url, data=body, headers=headers)
    resp = urllib.request.urlopen(req, timeout=90)
    data = json.loads(resp.read())
    msg = data["choices"][0]["message"]
    return (msg.get("content") or "") .strip()


def _parse_json(raw):
    # reasoning models may wrap the answer in prose; find every {...} mentioning fit_score
    best = None
    for m in re.finditer(r"\{[^{}]*\}", raw, re.S):
        try:
            d = json.loads(m.group(0))
        except Exception:
            continue
        if isinstance(d.get("fit_score"), (int, float)):
            best = d
            d["fit_score"] = int(d["fit_score"])
    return best


LAST_ERRORS = []

def _gate_once(provider_key_url, company, title, location, description):
    provider, key, url = provider_key_url
    prompt = _GATE_PROMPT.format(requirements=(description or "")[:3200], facts=_FACTS)
    for attempt in range(2):
        try:
            raw = _chat(url, key, provider, prompt, max_tokens=3000)
            d = _parse_json(raw)
            if d is not None and d.get("verdict") in ("PASS", "FAIL"):
                d["_model"] = provider
                return d
            return None
        except Exception as e:
            LAST_ERRORS.append("gate/" + provider.split("/")[-1] + ": " + type(e).__name__ + " " + str(e)[:100])
            if attempt < 1 and getattr(e, "code", None) in (429, 502, 503):
                time.sleep(4)
                continue
            return None


def _score_once(provider_key_url, company, title, location, description, retries=2):
    provider, key, url = provider_key_url
    prompt = _SCORE_PROMPT.format(facts=_FACTS, company=company, title=title, location=location or "n/a",
                            description=(description or "")[:3200])
    for attempt in range(retries + 1):
        try:
            raw = _chat(url, key, provider, prompt)
            d = _parse_json(raw)
            if d is not None:
                d["_model"] = provider
                return d
            return None
        except Exception as e:
            waitable = hasattr(e, "code") and getattr(e, "code") in (429, 502, 503)
            if attempt < retries and waitable:
                time.sleep(4 * (attempt + 1))
                continue
            return None


def _or_keys():
    names = ["OPENROUTER_API_KEY", "OPENROUTER_SWARM_API_KEY", "OPENROUTER_HERMES_API_KEY"]
    return [os.environ[n] for n in names if os.environ.get(n, "").strip()]


def llm_score(company: str, title: str, location: str, description: str) -> dict | None:
    results = []
    jobs_args = (company, title, location, description)
    or_keys = _or_keys()
    nv_key = os.environ.get("NVIDIA_API_KEY", "").strip()

    lanes = []
    ki = 0
    for model in FREE_MODELS[:2]:
        if not or_keys:
            break
        lanes.append(((model, or_keys[ki % len(or_keys)], OPENROUTER_URL), jobs_args))
        ki += 1
    if nv_key:
        lanes.append(((NV_MODEL, nv_key, NVIDIA_URL), jobs_args))

    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=4) as ex:
        # STAGE 1: hard-gate check (one strong lane is enough)
        gate_lane = ((NV_MODEL, nv_key, NVIDIA_URL), ) if nv_key else \
                    ((FREE_MODELS[0], or_keys[0], OPENROUTER_URL), )
        gfut = ex.submit(_gate_once, gate_lane[0], company, title, location, description)
        # STAGE 2: scoring lanes in parallel
        futs = [ex.submit(_score_once, lane[0], *lane[1]) for lane in lanes]
        verdict_gate = gfut.result(timeout=240)
        for f in futs:
            r = f.result(timeout=240)
            if r:
                results.append(r)

    if verdict_gate and verdict_gate.get("verdict") == "FAIL":
        out = {
            "fit_score": 15,
            "archetype": "hard-gated",
            "matched_strengths": [],
            "gaps": verdict_gate.get("unmet", [])[:4] or ["failed required qualification"],
            "lead_with": None,
            "rationale": "HARD GATE: " + (verdict_gate.get("notes") or "missing required credentials"),
            "gated": True,
            "model": "gate[" + verdict_gate.get("_model", "?").split("/")[-1] + "]",
        }
        return out

    if not results:
        return None

    scores = sorted(r["fit_score"] for r in results)
    if len(results) >= 3:
        verdict = [r for r in results if r["fit_score"] == scores[len(scores) // 2]][0]
        verdict["median_of"] = len(results)
    else:
        verdict = min(results, key=lambda r: abs(r["fit_score"] - scores[-1])) if False else \
                  min(results, key=lambda r: r["_model"] != "nvidia") if nv_key else results[0]

    out = dict(verdict)
    out["model"] = f"chain[{'+'.join(r['_model'].split('/')[-1].replace(':free','') for r in results)}]"
    out.pop("_model", None)
    return out
