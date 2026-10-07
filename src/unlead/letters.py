"""Opt-out letters. The paste section contains only the fields that site requires."""

from __future__ import annotations

from pathlib import Path

from unlead.catalog import by_id
from unlead.policy import LABELS, UnLeadError
from unlead.score import field_plan, supplied_from_case
from unlead.vault import selected_ids, write_private

_RESET_SUFFIXES = {".md", ".json"}


def reset_output(path: Path) -> None:
    if path.is_symlink():
        raise UnLeadError("Refusing to use a symlinked output directory.")
    path.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise UnLeadError("Refusing to use a symlinked output directory.")
    path.chmod(0o700)
    for child in path.iterdir():
        if child.is_symlink() or not child.is_file():
            continue
        if child.suffix in _RESET_SUFFIXES:
            child.unlink()


def _values(broker: dict, case: dict, send: list[str]) -> list[str]:
    identifiers = case["identifiers"]
    site = case.get("sites", {}).get(broker["id"], {})
    lines = []
    for field in send:
        if field == "profile_url":
            value = site.get("profile_url", "")
        else:
            value = identifiers.get(field, "")
        if not value:
            raise UnLeadError("A letter field has no value.")
        lines.append(f"- {LABELS[field]}: {value}")
    return lines


def _seen_sentence(site: dict) -> str:
    seen = site.get("seen") or "unconfirmed"
    holdings = site.get("holdings") or []
    if seen == "yes" and holdings:
        categories = ", ".join(holdings)
        return (
            f"I looked at a page that matched me and saw these categories: {categories}. "
            "This is a category list, not a copy of the page."
        )
    if seen == "no":
        return (
            "I looked and did not find a listing. If you have no matching record, "
            "discard this request and do not create one."
        )
    return (
        "I have not confirmed a listing. Match only an existing record. "
        "If none matches, discard this request and do not create one."
    )


def render_letter(broker: dict, case: dict, plan: dict) -> str:
    site = case.get("sites", {}).get(broker["id"], {})
    withheld = ", ".join(plan["withheld"]) or "nothing"
    body = [
        "I am the person this request is about. I am writing about my own record.",
        "",
        "Please delete the personal information you hold about me, stop selling it, and stop sharing it. "
        "Apply your published opt-out. Where a state privacy law applies to me, treat this as a request "
        "to delete and to opt out of sale and sharing, including the California Consumer Privacy Act "
        "as amended by the CPRA.",
        "",
        "Use the identifiers below only to match a record you already have. If nothing matches, "
        "discard this request. Do not create a record from it. Do not add these identifiers to a "
        "marketing list, a people-search profile, or a lead file.",
        "",
        "Identifiers:",
        *_values(broker, case, plan["send"]),
        "",
        _seen_sentence(site),
        "",
        "Do not ask me for a Social Security number, a government ID, a date of birth, a password, "
        "a payment card, or a biometric. If your process requires a field that is not listed above, "
        "reply with the name of that field and wait.",
        "",
        "This request does not authorize you to look up any other person, or to search for more information about me.",
    ]
    if "optout_email" in plan["send"]:
        email = case["identifiers"]["optout_email"]
        body.extend(
            [
                "",
                f"Send the confirmation only to {email}. Do not enroll that address in marketing.",
            ]
        )
    paste = "\n".join(body)
    header = [
        f"# {broker['name']}",
        "",
        "Local file. Paste only the section under the heading into a message box.",
        f"Opt-out page: {broker['opt_out_url']}",
        f"Fields in the request: {', '.join(plan['send'])}",
        f"Withheld from this request: {withheld}",
        "",
        "## Paste this",
        "",
        paste,
        "",
    ]
    return "\n".join(header)


def render_gap(broker: dict, missing: list[str]) -> str:
    fields = ", ".join(missing)
    return (
        f"# {broker['name']} — not ready\n\n"
        f"Missing: {fields}\n\n"
        "Do not submit this site yet. Add the missing fields with `unlead ask` or `unlead id set`. "
        "A listing URL is `unlead holdings`.\n\n"
        f"Opt-out page, once the packet is ready: {broker['opt_out_url']}\n"
    )


def render_manual(broker: dict) -> str:
    notes = broker["notes"].strip()
    return (
        f"# {broker['name']} — do this yourself\n\n"
        "No agent packet. This file contains no identifiers from your case.\n\n"
        f"Page: {broker['opt_out_url']}\n\n"
        f"{notes}\n\n"
        "If the page asks for a Social Security number, a date of birth, a government ID, "
        "or a face photo, type those only on this official page and only if you still want to file. "
        "Do not put them in a chat agent.\n"
    )


def _selected(case: dict) -> list[dict]:
    brokers = [by_id(broker_id) for broker_id in selected_ids(case)]
    brokers.sort(key=lambda broker: (broker["tier"], broker["name"].casefold()))
    return brokers


def write_letters(directory: Path, case: dict, include_optional: bool = False) -> list[Path]:
    out = directory / "letters"
    reset_output(out)
    brokers = _selected(case)
    lines = ["# Letters", ""]
    written = []
    if not brokers:
        lines.append("No sites selected.")
        write_private(out / "INDEX.md", "\n".join(lines) + "\n")
        return []
    for broker in brokers:
        if broker["status"] == "closed":
            lines.append(f"- {broker['name']}: closed, nothing written")
            continue
        path = out / f"{broker['id']}.md"
        if broker["status"] == "human_only":
            text = render_manual(broker)
            state = "manual, no identifiers in the file"
        else:
            plan = field_plan(broker, supplied_from_case(case, broker["id"]), include_optional)
            if plan["letter_ready"]:
                text = render_letter(broker, case, plan)
                state = "ready: " + ", ".join(plan["send"])
            else:
                text = render_gap(broker, plan["missing"])
                state = "missing: " + ", ".join(plan["missing"])
        write_private(path, text)
        written.append(path)
        lines.append(f"- {broker['name']}: {state}")
    lines.append("")
    write_private(out / "INDEX.md", "\n".join(lines) + "\n")
    return written
