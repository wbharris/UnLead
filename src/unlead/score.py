"""Score a field set against the catalog. No network, no second person."""

from __future__ import annotations

from dataclasses import dataclass

from unlead.catalog import by_id, catalog
from unlead.policy import FIELD_ORDER, PROMPTS

NAME_AND_PHONE = (
    "Name and phone are enough for you to tell your own row from someone else who shares your name. "
    "The phone is the part that separates the rows."
)
NAME_ONLY = (
    "A name by itself matches other people. One phone number is the smallest extra fact that picks out your row."
)
PHONE_ONLY = (
    "A phone number can single out a row on a reverse-lookup site. "
    "Add your name before you rely on a row, so you can reject one that is not yours."
)
NONE_YET = "Add your name and one phone number. That pair is the starting set for spotting your own listing."

SPLIT = (
    "Spotting your row and filing the opt-out use different fields. "
    "A field can identify your row and still stay out of a request when that site's form does not need it."
)


@dataclass
class Question:
    field: str
    prompt: str
    brokers: list[str]
    broker_id: str | None = None


def supplied_from_case(case: dict, broker_id: str | None = None) -> set[str]:
    fields = {key for key, value in case.get("identifiers", {}).items() if value}
    if broker_id:
        site = case.get("sites", {}).get(broker_id) or {}
        if site.get("profile_url"):
            fields.add("profile_url")
    return fields


def field_plan(broker: dict, supplied: set[str], include_optional: bool = False) -> dict:
    allowed = set(broker["form_requires"]) | set(broker["match_with"])
    if include_optional:
        allowed |= set(broker["form_optional"])
    send = [field for field in FIELD_ORDER if field in allowed and field in supplied]
    withheld = [field for field in FIELD_ORDER if field in supplied and field not in set(send)]
    missing = [field for field in broker["form_requires"] if field not in supplied]
    letter_ready = broker["status"] == "open" and not missing
    return {
        "send": send,
        "withheld": withheld,
        "missing": missing,
        "letter_ready": letter_ready,
        "agent_ready": letter_ready and bool(broker["agent_allowed"]),
    }


def recognition(supplied: set[str]) -> tuple[str, str]:
    has_name = "legal_name" in supplied
    has_phone = "phone" in supplied
    if has_name and has_phone:
        return "name_phone", NAME_AND_PHONE
    if has_name:
        return "name_only", NAME_ONLY
    if has_phone:
        return "phone_only", PHONE_ONLY
    return "none", NONE_YET


def score_catalog(case: dict | None = None, assume: set[str] | None = None, include_optional: bool = False) -> list[dict]:
    rows = []
    for broker in catalog():
        if assume is not None:
            supplied = set(assume)
        elif case is not None:
            supplied = supplied_from_case(case, broker["id"])
        else:
            supplied = set()
        plan = field_plan(broker, supplied, include_optional)
        rows.append(
            {
                "id": broker["id"],
                "name": broker["name"],
                "status": broker["status"],
                "kind": broker["kind"],
                "tier": broker["tier"],
                **plan,
            }
        )
    rows.sort(key=lambda row: (row["tier"], row["name"].casefold()))
    return rows


def questions_for(case: dict) -> list[Question]:
    needed: dict[str, list[str]] = {}
    url_questions: list[Question] = []
    selected = []
    for broker_id, site in case.get("sites", {}).items():
        if not site.get("selected"):
            continue
        broker = by_id(broker_id)
        if broker["status"] != "open":
            continue
        selected.append(broker)
    selected.sort(key=lambda broker: (broker["tier"], broker["name"].casefold()))
    for broker in selected:
        plan = field_plan(broker, supplied_from_case(case, broker["id"]))
        for field in plan["missing"]:
            if field == "profile_url":
                url_questions.append(
                    Question(
                        field="profile_url",
                        prompt=PROMPTS["profile_url"].format(name=broker["name"]),
                        brokers=[broker["name"]],
                        broker_id=broker["id"],
                    )
                )
            else:
                needed.setdefault(field, []).append(broker["name"])
    questions = []
    for field in FIELD_ORDER:
        if field == "profile_url" or field not in needed:
            continue
        questions.append(Question(field=field, prompt=PROMPTS[field], brokers=needed[field]))
    questions.extend(url_questions)
    return questions


def format_probe(rows: list[dict], supplied: set[str]) -> str:
    _level, text = recognition(supplied)
    ready = [row for row in rows if row["agent_ready"]]
    waiting = [row for row in rows if row["status"] == "open" and not row["agent_ready"]]
    manual = [row for row in rows if row["status"] == "human_only"]
    closed = [row for row in rows if row["status"] == "closed"]
    lines = [text, "", SPLIT, ""]
    lines.append(f"Ready for a letter and an agent packet ({len(ready)})")
    lines.extend(_ready_line(row) for row in ready)
    if not ready:
        lines.append("  none")
    lines.append("")
    lines.append(f"Need more before a letter ({len(waiting)})")
    lines.extend(_waiting_line(row) for row in waiting)
    if not waiting:
        lines.append("  none")
    lines.append("")
    lines.append(f"File yourself. No agent packet ({len(manual)})")
    lines.extend(f"  {row['name']}: `unlead guide {row['id']}`" for row in manual)
    lines.append("")
    lines.append(f"Do not open ({len(closed)})")
    lines.extend(f"  {row['name']}" for row in closed)
    lines.append("")
    return "\n".join(lines)


def _ready_line(row: dict) -> str:
    send = ", ".join(row["send"]) or "nothing"
    withheld = ", ".join(row["withheld"]) or "nothing"
    return f"  {row['name']}: send {send}; withhold {withheld}"


def _waiting_line(row: dict) -> str:
    missing = ", ".join(row["missing"]) or "nothing"
    withheld = ", ".join(row["withheld"]) or "nothing"
    return f"  {row['name']}: missing {missing}; withhold {withheld}"
