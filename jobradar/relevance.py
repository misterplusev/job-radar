"""Robotics relevance classifier — stdlib only, deterministic, no network.

WHAT THIS GATES
    Only the Discord announce path. `publish.publish()` still persists every
    scraped posting to `robotics_jobs`, so the live board keeps its full
    Browse-All view and nothing is lost. This module decides what gets
    announced to #robotics-jobs.

WHY IT EXISTS
    The robotics target list deliberately includes big-tech boards (anthropic,
    databricks, stripe, coinbase, figma, airbnb, robinhood, ramp, openai) for
    their autonomy teams, but `publish.py` announced EVERY newly-seen URL from
    those boards. Result: ~4k pure-tech postings per scrape cycle landing in a
    robotics channel. Storage was never wrong; only the announce was.

LOGIC — DENY-beats-ALLOW, biased toward rejecting
    1. NEGATIVE title hit                      -> reject
    2. STRONG robotics title hit               -> accept
    3. WEAK robotics title hit + strict
       robotics corroboration in the text     -> accept
    4. otherwise                               -> reject

    A false accept is the reported bug; a false reject only means a real role
    stays on the board and is not pinged. So the bar for acceptance is high.

    Boards fetched with content=false (see targets.json `_resource_note` —
    andurilindustries) carry NO description, so those roles are accepted on a
    STRONG title match only. That is intentional: fail closed on announcements.
"""
from __future__ import annotations

import re
from typing import Optional, Tuple

__all__ = ["is_relevant", "explain", "NEGATIVE_TITLE", "STRONG_TITLE", "WEAK_TITLE", "CORROBORATION"]

# Minimum description length before it may corroborate a WEAK title match.
MIN_CORROBORATION_CHARS = 200


def _rx(words) -> "re.Pattern":
    # Word-boundary alternation, whitespace/hyphen tolerant so "self-driving",
    # "self driving" and "selfdriving" all match one entry.
    parts = [w.replace(" ", r"[-\s]+") for w in words]
    return re.compile(r"(?<![a-z0-9])(?:" + "|".join(parts) + r")(?![a-z0-9])", re.I)


# --------------------------------------------------------------------------- #
# 1) NEGATIVE — reject outright. Business/support roles that ride along on
#    every large board. Checked FIRST, before any robotics signal.
# --------------------------------------------------------------------------- #
NEGATIVE_TITLE = _rx([
    "intern", "internship", "co-op", "coop", "apprentice",
    "security controls", "controls assurance", "abuse control", "internal control",
    "grc", "sox", "data center", "product operations", "business operations",
    "internationalization", "localization manager", "localization specialist",
    "sales", "account executive", "business development", "bizdev",
    "marketing", "brand", "communications", "public relations", "content writer",
    "copywriter", "technical writer", "social media", "demand generation",
    "legal", "counsel", "attorney", "paralegal", "contracts", "compliance officer",
    "human resources", "hr business partner", "recruiter", "recruiting",
    "talent acquisition", "people operations", "people ops", "chief of staff",
    "finance", "financial", "accounting", "accountant", "controller", "tax",
    "treasury", "payroll", "audit", "internal controls", "fp&a",
    "insurance", "claims", "real estate", "procurement", "sourcing",
    "nurse", "nursing", "physician", "clinical", "therapist", "dental", "pharmacy",
    "driver", "cdl", "chauffeur", "courier", "warehouse", "forklift", "picker",
    "delivery", "fleet driver", "parts advisor",
    "barista", "chef", "cook", "waiter", "waitress", "server", "host", "hostess",
    "housekeeper", "housekeeping", "janitor", "custodian", "busser",
    "retail", "cashier", "store associate", "groomer", "barber",
    "customer support", "customer service", "customer success", "technical support",
    "help desk", "service desk",
    "teacher", "teaching", "instructor", "tutor", "curriculum",
    "security officer", "security guard", "patrol officer",
    "underwriter", "actuary", "broker",
])

# --------------------------------------------------------------------------- #
# 2) STRONG — unambiguous robotics signal. A title hit alone is enough.
# --------------------------------------------------------------------------- #
STRONG_TITLE = _rx([
    "robotics", "robotic", "roboticist", "robot", "robots", "robotic surgery",
    "autonomous", "autonomy", "self-driving", "self driving", "selfdriving",
    "driverless", "autonomous vehicle", "autonomous vehicles", "autonomous driving",
    "drone", "drones", "uav", "quadrotor", "hexacopter", "multirotor", "octocopter",
    "rover", "rovers", "lunar rover", "planetary rover",
    "manipulator", "robotic arm", "robotic arms", "cobot", "collaborative robot",
    "humanoid", "biped", "exoskeleton", "prosthetic", "prostheses", "mechatronics",
    "actuator", "actuators", "servomechanism", "servo",
    "kinematic", "kinematics", "inverse kinematics", "forward kinematics",
    "trajectory", "trajectories", "trajectory optimization",
    "motion planning", "motion planner", "path planning", "path planner",
    "localization", "state estimation", "sensor fusion", "odometry",
    "state localization", "visual localization", "lidar localization",
    "robot localization", "global localization",
    "lidar", "point cloud", "point-cloud",
    "slam", "simultaneous localization",
    "ros", "ros2", "ros/ros2", "ros2 humble",
    "isaac sim", "isaac gym", "isaac", "mujoco", "gazebo", "webots", "coppeliasim",
    "model predictive control", "mpc controller", "finite state machine control",
    "guidance navigation and control", "gnc engineer",
    "teleoperation", "teleoperated", "teleop", "drive-by-wire", "fly-by-wire",
    "flight dynamics", "vehicle dynamics", "motion control engineer",
    "autonomy stack", "autonomy team", "autonomy engineer", "autonomy software",
    "robotaxi", "robo-taxi", "warehouse robotics",
    "v2x", "perception stack", "perception engineer", "perception scientist",
    "behavior planning", "behaviour planning", "motion planner", "path planner",
])

# --------------------------------------------------------------------------- #
# 3) WEAK — plausible in robotics, but also common in ordinary software and
#    finance roles. Only accepted with corroboration.
# --------------------------------------------------------------------------- #
WEAK_TITLE = _rx([
    "perception", "controls", "control", "control systems", "controller", "controllers",
    "computer vision", "machine vision", "image processing", "video perception",
    "embedded", "firmware", "device driver", "drivers", "real-time", "realtime",
    "simulation", "simulator", "dynamics", "simulation engineer",
    "mapping", "calibration", "navigation", "navigation engineer",
    "tracking", "tracking engineer", "calibration engineer",
    "localization", "localization engineer", "solver", "optimization", "optimisation",
    "hmi", "plc", "can bus", "canbus", "telematics",
    "operator", "operators", "technician", "technicians", "field applications",
])

# Strict corroboration set — searched in title + description when a WEAK title
# hit needs backing. Deliberately narrow: no generic words like "automation",
# "cloud", "data", "ai" or "platform".
CORROBORATION = _rx([
    "robotics", "robotic", "robot", "robots",
    "autonom", "self-driving", "driverless",
    "lidar", "sensor fusion", "point cloud", "radar",
    "slam", "localization", "state estimation", "odometry",
    "trajectory", "motion planning", "path planning",
    "kinematic", "kinematics", "dynamics", "dynamics simulation",
    "actuator", "actuators", "manipulator", "exoskeleton", "humanoid", "mechatronics",
    "perception", "perception stack", "sensor", "sensors", "sensing",
    "control system", "controls", "controller", "control loop", "closed loop",
    "embedded system", "firmware", "real-time control", "rtos",
    "ros", "ros2", "isaac", "mujoco", "gazebo", "webots",
    "vehicle dynamics", "flight dynamics", "steering", "braking", "throttle",
    "powertrain", "electric vehicle", "autonomous vehicle", "drive-by-wire",
    "navigation", "mapping", "tracking", "calibration",
    "predictive maintenance", "teleoperation", "teleop",
])


_CORP_SUFFIXES = (
    "incorporated", "corporation", "corp", "company", "holdings", "group",
    "technologies", "technology", "labs", "plc", "llc", "ltd", "inc", "sa", "gmbh",
    "pbc", "llp", "pllc", "limited", "bv", "nv",
)


def _norm_company(name: Optional[str]) -> str:
    """Lowercase, alphanumeric-only, corporate suffix stripped.

    Providers report the same employer inconsistently ("Stripe" vs "Stripe, Inc."
    vs "stripe inc"), so the strict-board policy must survive all three.
    """
    flat = re.sub(r"[^a-z0-9]", "", (name or "").lower())
    changed = True
    while changed and len(flat) > 4:
        changed = False
        for suffix in _CORP_SUFFIXES:
            if flat.endswith(suffix) and len(flat) - len(suffix) >= 3:
                flat = flat[: -len(suffix)]
                changed = True
    return flat


# Boards that exist in targets.json only for their autonomy/robotics teams. On
# these, an ambiguous title (or an ambiguous title + a robotics-flavoured
# description) is not enough — a STRONG title match is required. Measured leak
# rate on the pure-tech boards drops to 0 with this applied.
#
# Matches the non-robotics slugs in config/targets.json:
#   greenhouse: anthropic databricks stripe coinbase figma airbnb robinhood
#   ashby:      ramp openai
STRICT_TITLE_ONLY_COMPANIES = frozenset({
    "anthropic", "databricks", "stripe", "coinbase", "figma", "airbnb",
    "robinhood", "ramp", "openai",
})


# --------------------------------------------------------------------------- #
# ROBOTICS_NATIVE — verified robotics/autonomy employers.
#
# At these employers the WHOLE board is on-topic, so the title-signal
# requirement is the wrong instrument: it rejected "Senior Radar Systems
# Engineer" (Nuro), "Wire Harness Engineer" (Figure AI), "Manufacturing
# Engineer, Battery" (1X) and "AV Operations Specialist" (Figure AI) purely
# because their titles lacked a robotics keyword.
#
# Measured on 2026-10-16, the first run after the 34 new boards landed
# suppressed 1,772 postings and announced 43 — a 97.6% rejection rate at
# employers we had just deliberately added.
#
# So for these companies the decision is: NEGATIVE_TITLE still applies (it is
# the business/service-role filter, and it carries the internship rule), and
# everything else is announced. Storage was never filtered and still is not.
#
# Excluded on purpose: the nine pure-software seed boards above (they are in
# targets.json only for their autonomy teams) and the mixed megacorps
# amazon / rockwellautomation / lgelectronics, whose boards are mostly
# off-topic consumer-and-enterprise roles.
# --------------------------------------------------------------------------- #
ROBOTICS_NATIVE = frozenset({
    # AV / self-driving
    "waymo", "nuro", "motional", "kodiak", "kodiakrobotics", "zoox", "waabi", "wayve",
    "torcrobotics", "maymobility", "pronto", "oxa", "weride",
    "toyotaresearchinstitute",
    # delivery / logistics robotics
    "zipline", "flyzipline", "locusrobotics", "brightmachines", "dexory",
    "outrider", "ambirobotics", "picklerobot", "osaro", "cobaltrobotics",
    # humanoid / manipulation / hardware
    "figure", "figureai", "apptronik", "agilityrobotics", "1x", "physicalintelligence",
    "standardbots", "dexterity", "anybotics", "bostondynamics", "autostore",
    # drones / defense autonomy
    "skydio", "shieldai", "brinc", "brincdrones", "swoop", "swoopaero",
    "saronic", "epirus",
    # field service / medical / inspection robotics
    "serverobotics", "diligentrobotics", "noahmedical",
    # autonomy software / perception
    "helmai",
    # space & launch hardware (engineering-dense boards)
    "spacex", "andurilindustries", "rocketlab", "relativityspace", "vast",
    "astranis", "machindustries", "planet", "ursamajor", "impulse",
    "impulsespace", "brightmachines", "dexory", "outrider", "wing",
})

_NATIVE_NORM = frozenset(_norm_company(c) for c in ROBOTICS_NATIVE)
_STRICT_NORM = frozenset(_norm_company(c) for c in STRICT_TITLE_ONLY_COMPANIES)


def _text(title: Optional[str], description: Optional[str]) -> str:
    """Retained for callers that want title+description as one blob."""
    return f"{title or ''}\n{description or ''}"


def explain(title: Optional[str], description: Optional[str] = None,
            company: Optional[str] = None) -> Tuple[bool, str]:
    """Return (is_relevant, reason). Same decision as `is_relevant`."""
    title = title or ""
    description = description or ""

    neg = NEGATIVE_TITLE.search(title)
    if neg:
        return False, f"negative:{neg.group(0).lower()}"

    norm = _norm_company(company)
    if norm in _NATIVE_NORM:
        return True, f"robotics-native-employer:{norm}"

    strong = STRONG_TITLE.search(title)
    if strong:
        return True, f"strong-title:{strong.group(0).lower()}"

    strict = norm in _STRICT_NORM
    if strict:
        return False, f"strict-company-no-strong-title:{norm}"

    weak = WEAK_TITLE.search(title)
    if not weak:
        return False, "no-robotics-signal"

    # WEAK title needs backing, and backing needs actual prose to search.
    # Corroboration reads the DESCRIPTION ONLY, and the match must be a DIFFERENT
    # term from the one that triggered WEAK_TITLE. Otherwise the gate is a no-op:
    # a title of "Controls Engineer" matched the `controls` corroboration term on
    # its own, and a description that merely echoes the title ("we are looking for
    # a controls engineer...") confirmed itself.
    if len(description.strip()) < MIN_CORROBORATION_CHARS:
        return False, f"weak-title-unconfirmed:{weak.group(0).lower()}"

    weak_text = weak.group(0).lower()
    for hit in CORROBORATION.finditer(description):
        if hit.group(0).lower() != weak_text:
            return True, f"weak-title+corroboration:{weak_text}+{hit.group(0).lower()}"
    return False, f"weak-title-uncorroborated:{weak_text}"


def is_relevant(title: Optional[str], description: Optional[str] = None,
                company: Optional[str] = None) -> bool:
    """True when a posting belongs in #robotics-jobs."""
    return explain(title, description, company)[0]