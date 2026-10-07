"""Local case file. Mode 0600. One subject: the person operating Unlead."""

from __future__ import annotations

import json
import os
import subprocess
from datetime import date, timedelta
from pathlib import Path

from unlead.policy import (
    FORBIDDEN_KEYS,
    IDENTIFIER_FIELDS,
    UnleadError,
    validate_holdings,
    validate_identifier,
    validate_profile_url,
)

_SITE_DEFAULT = {
    "selected": False,
    "seen": "unconfirmed",
    "holdings": [],
    "profile_url": "",
    "status": "draft",
    "submitted_on": "",
    "confirmed_on": "",
}


def case_path(directory: Path) -> Path:
    return directory / "case.json"


def _refuse_symlink(path: Path, label: str) -> None:
    if path.is_symlink():
        raise UnleadError(f"Refusing to use a symlinked {label}.")


def ensure_private_dir(path: Path) -> None:
    _refuse_symlink(path, "directory")
    path.mkdir(parents=True, exist_ok=True)
    _refuse_symlink(path, "directory")
    os.chmod(path, 0o700)


def write_private(path: Path, text: str) -> None:
    _refuse_symlink(path, "file")
    ensure_private_dir(path.parent)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        os.write(fd, text.encode("utf-8"))
    finally:
        os.close(fd)
    os.chmod(path, 0o600)


def new_case() -> dict:
    return {
        "schema": 1,
        "subject": "self",
        "identifiers": {},
        "sites": {},
    }


def _check_shape(data: dict) -> None:
    if data.get("schema") != 1 or data.get("subject") != "self":
        raise UnleadError("This case is not an Unlead file for your own opt-out.")
    identifiers = data.get("identifiers")
    if not isinstance(identifiers, dict):
        raise UnleadError("Case identifiers are unreadable.")
    for key in identifiers:
        if key in FORBIDDEN_KEYS or key not in IDENTIFIER_FIELDS:
            raise UnleadError("Case file contains a field Unlead will not keep.")


def load_case(directory: Path) -> dict:
    path = case_path(directory)
    _refuse_symlink(directory, "directory")
    _refuse_symlink(path, "case file")
    if not path.is_file():
        raise UnleadError(f"No case at {directory}. Run `unlead init --case {directory}`.")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise UnleadError("Case file is not valid JSON.") from exc
    _check_shape(data)
    data.setdefault("sites", {})
    return data


def save_case(directory: Path, data: dict) -> None:
    _check_shape(data)
    write_private(case_path(directory), json.dumps(data, indent=2) + "\n")


def init_case(directory: Path, identifiers: dict[str, str]) -> dict:
    path = case_path(directory)
    if path.exists() or path.is_symlink():
        raise UnleadError("A case already exists there.")
    data = new_case()
    for key, value in identifiers.items():
        data["identifiers"][key] = validate_identifier(key, value)
    if "legal_name" not in data["identifiers"] or "phone" not in data["identifiers"]:
        raise UnleadError("Init needs your name and one phone number.")
    save_case(directory, data)
    write_private(
        directory / "README.txt",
        "Unlead case. Local opt-out file for your own listings. Do not commit this directory.\n",
    )
    return data


def set_identifier(case: dict, key: str, value: str) -> None:
    case["identifiers"][key] = validate_identifier(key, value)


def unset_identifier(case: dict, key: str) -> None:
    if key in FORBIDDEN_KEYS:
        raise UnleadError("Unlead does not store that.")
    if key not in IDENTIFIER_FIELDS:
        raise UnleadError(f"Unknown field {key}.")
    case["identifiers"].pop(key, None)


def _site(case: dict, broker_id: str) -> dict:
    sites = case.setdefault("sites", {})
    if broker_id not in sites:
        sites[broker_id] = dict(_SITE_DEFAULT)
        sites[broker_id]["holdings"] = []
    return sites[broker_id]


def select_site(case: dict, broker: dict) -> bool:
    """Select a site. Return True if it was already selected."""
    if broker["status"] == "closed":
        raise UnleadError(
            f"{broker['name']} is closed. Do not open the old domain. `unlead sites {broker['id']}` has the reason."
        )
    record = _site(case, broker["id"])
    already = bool(record.get("selected"))
    record["selected"] = True
    return already


def unselect_site(case: dict, broker_id: str) -> None:
    record = case.get("sites", {}).get(broker_id)
    if record:
        record["selected"] = False


def set_holdings(case: dict, broker: dict, seen: str | None = None, holdings: list[str] | None = None, url: str | None = None) -> None:
    if broker["status"] == "closed":
        raise UnleadError(f"{broker['name']} is closed. Do not open the old domain.")
    record = _site(case, broker["id"])
    record["selected"] = True
    if seen is not None:
        if seen not in {"yes", "no", "unconfirmed"}:
            raise UnleadError("Seen must be yes, no, or unconfirmed.")
        record["seen"] = seen
    if holdings is not None:
        record["holdings"] = validate_holdings(holdings)
    if url is not None:
        record["profile_url"] = validate_profile_url(url, broker)


def mark_site(case: dict, broker: dict, status: str, day: str) -> None:
    if broker["status"] == "closed":
        raise UnleadError(f"{broker['name']} is closed.")
    if status not in {"draft", "submitted", "confirmed"}:
        raise UnleadError("Mark status must be draft, submitted, or confirmed.")
    try:
        date.fromisoformat(day)
    except ValueError as exc:
        raise UnleadError("Date must be YYYY-MM-DD.") from exc
    record = _site(case, broker["id"])
    if not record.get("selected"):
        raise UnleadError("Select the site before marking it.")
    record["status"] = status
    if status == "draft":
        record["submitted_on"] = ""
        record["confirmed_on"] = ""
    elif status == "submitted":
        record["submitted_on"] = day
        record["confirmed_on"] = ""
    else:
        record["confirmed_on"] = day
        if not record.get("submitted_on"):
            record["submitted_on"] = day


def recheck_on(record: dict, broker: dict) -> str:
    days = broker.get("recheck_days") or 0
    if not days:
        return ""
    base = record.get("confirmed_on") or record.get("submitted_on")
    if not base:
        return ""
    return (date.fromisoformat(base) + timedelta(days=days)).isoformat()


def selected_ids(case: dict) -> list[str]:
    return [broker_id for broker_id, record in case.get("sites", {}).items() if record.get("selected")]


def mode_problem(directory: Path) -> str | None:
    path = case_path(directory)
    problems = []
    file_mode = path.stat().st_mode & 0o777
    dir_mode = directory.stat().st_mode & 0o777
    if file_mode != 0o600:
        problems.append(f"case.json mode is {oct(file_mode)}, expected 0o600")
    if dir_mode != 0o700:
        problems.append(f"case directory mode is {oct(dir_mode)}, expected 0o700")
    if not problems:
        return None
    return "; ".join(problems)


def unignored_warning(directory: Path) -> str | None:
    """Warn when a case sits in a git tree that would commit it."""
    try:
        resolved = directory.resolve()
    except OSError:
        return None
    git_root = None
    for parent in [resolved, *resolved.parents]:
        if (parent / ".git").exists():
            git_root = parent
            break
    if git_root is None:
        return None
    try:
        result = subprocess.run(
            ["git", "-C", str(git_root), "check-ignore", "-q", str(resolved)],
            check=False,
            capture_output=True,
        )
    except OSError:
        return None
    if result.returncode == 0:
        return None
    return (
        "This case directory is inside a git repo and is not ignored. "
        "Move it, or ignore it, before you commit."
    )


