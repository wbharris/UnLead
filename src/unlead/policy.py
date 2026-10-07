"""Field rules. The case stores a small allowlist and never a second person."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlsplit

ALLOWED_FIELDS = (
    "legal_name",
    "phone",
    "optout_email",
    "city",
    "state",
    "postal_code",
    "profile_url",
)
IDENTIFIER_FIELDS = (
    "legal_name",
    "phone",
    "optout_email",
    "city",
    "state",
    "postal_code",
)
FIELD_ORDER = ALLOWED_FIELDS

HOLDING_CATEGORIES = (
    "name",
    "phone",
    "email",
    "address",
    "relatives",
    "age",
    "employer",
    "photo",
)

# Asked for by name so an agent stops. These values are never stored.
GLOBAL_STOP = (
    "Social Security number",
    "government ID",
    "driver license",
    "passport",
    "date of birth",
    "password",
    "payment card",
    "bank account",
    "mother's maiden name",
    "a photo of your face",
    "a biometric",
    "a different person's name",
    "a relative's information",
)

FORBIDDEN_KEYS = {
    "ssn",
    "social_security",
    "social_security_number",
    "dob",
    "date_of_birth",
    "birthdate",
    "government_id",
    "drivers_license",
    "driver_license",
    "passport",
    "password",
    "maiden_name",
    "biometric",
    "selfie",
    "credit_card",
    "bank_account",
}

LABELS = {
    "legal_name": "Name",
    "phone": "Phone",
    "optout_email": "Email for this request only",
    "city": "City",
    "state": "State",
    "postal_code": "Postal code",
    "profile_url": "Profile URL",
}

PROMPTS = {
    "legal_name": (
        "Your legal name. Stored only in this case file. "
        "A letter includes it only when that site's opt-out uses a name to match the row."
    ),
    "phone": (
        "One phone number you already use. Stored only in this case file. "
        "It is how you tell your row from another person with the same name. "
        "A letter includes it only when that site's opt-out uses a phone to match the row."
    ),
    "optout_email": (
        "An email for the confirmation link. A separate opt-out inbox keeps this address "
        "off your main mail. Press Enter to skip."
    ),
    "city": "City. Press Enter to skip. Brokers that require a city stay unready.",
    "state": "State. Press Enter to skip. Brokers that require a state stay unready.",
    "postal_code": (
        "Postal code. Press Enter to skip. Brokers that require a postal code stay unready."
    ),
    "profile_url": (
        "The https address of your own listing on {name}. "
        "Copy it from the address bar of that listing. Press Enter to skip {name}."
    ),
}

_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_NETWORK_IMPORTS = (
    "requests",
    "httpx",
    "aiohttp",
    "selenium",
    "playwright",
    "scrapy",
    "mechanize",
    "urllib.request",
    "http.client",
    "socket",
)


class UnLeadError(ValueError):
    """A problem the user can fix. The message must not echo a secret they typed."""


def clean_line(value: str, label: str, limit: int = 200) -> str:
    if not isinstance(value, str):
        raise UnLeadError(f"{label} must be text.")
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in value):
        raise UnLeadError(f"{label} must be a single line.")
    text = value.strip()
    if not text:
        raise UnLeadError(f"{label} is empty.")
    if len(text) > limit:
        raise UnLeadError(f"{label} is too long.")
    return text


def validate_name(value: str) -> str:
    text = clean_line(value, "Name", 120)
    if any(ch.isdigit() for ch in text):
        raise UnLeadError("A name does not include digits.")
    folded = text.casefold()
    if " and " in folded or " & " in text or ";" in text:
        raise UnLeadError("Use one person's name. This case is for your own opt-out.")
    if len(text) < 3:
        raise UnLeadError("Name is too short.")
    return text


def validate_phone(value: str) -> str:
    text = clean_line(value, "Phone", 40)
    if any(ch not in "0123456789 +-()." for ch in text):
        raise UnLeadError("Phone may contain digits, spaces, and + - ( ) .")
    digits = "".join(ch for ch in text if ch.isdigit())
    if len(digits) < 10 or len(digits) > 15:
        raise UnLeadError("Use one phone number, 10 to 15 digits.")
    return text


def validate_email(value: str) -> str:
    text = clean_line(value, "Email")
    if text.count("@") != 1 or " " in text:
        raise UnLeadError("Email needs a single @ and no spaces.")
    local, domain = text.split("@")
    if not local or "." not in domain or domain.startswith(".") or domain.endswith("."):
        raise UnLeadError("Email does not look usable.")
    return text


def validate_place(value: str, label: str) -> str:
    return clean_line(value, label, 80)


def validate_identifier(key: str, value: str) -> str:
    if key in FORBIDDEN_KEYS:
        raise UnLeadError(
            "UnLead does not store that. "
            "Social Security numbers, dates of birth, IDs, passwords, and biometrics stay out of the case."
        )
    if key not in IDENTIFIER_FIELDS:
        raise UnLeadError(f"Unknown field {key}.")
    if key == "legal_name":
        return validate_name(value)
    if key == "phone":
        return validate_phone(value)
    if key == "optout_email":
        return validate_email(value)
    if key == "state":
        return validate_place(value, "State")
    if key == "city":
        return validate_place(value, "City")
    if key == "postal_code":
        return validate_place(value, "Postal code")
    raise UnLeadError(f"Unknown field {key}.")


def host_allowed(host: str, suffixes: list[str]) -> bool:
    host = (host or "").casefold().rstrip(".")
    if not host or ".." in host:
        return False
    for suffix in suffixes:
        item = suffix.casefold().rstrip(".")
        if host == item or host.endswith("." + item):
            return True
    return False


def validate_profile_url(url: str, broker: dict) -> str:
    text = clean_line(url, "Profile URL", 500)
    parts = urlsplit(text)
    if parts.scheme != "https" or not parts.hostname:
        raise UnLeadError("Profile URL must be an https address.")
    if parts.username or parts.password:
        raise UnLeadError("Profile URL must not include a username or password.")
    if parts.query or parts.fragment:
        raise UnLeadError("Paste the listing path without a query string or fragment.")
    if not host_allowed(parts.hostname, broker["allowed_hosts"]):
        raise UnLeadError(
            f"That host is not {broker['name']}. Paste a listing on that broker's own site, or skip."
        )
    return text


def validate_holdings(categories: list[str]) -> list[str]:
    cleaned = []
    for item in categories:
        text = clean_line(item, "Holding", 40).casefold()
        if text not in HOLDING_CATEGORIES:
            allowed = ", ".join(HOLDING_CATEGORIES)
            raise UnLeadError(f"Holdings are categories ({allowed}), not a copy of the page.")
        if text not in cleaned:
            cleaned.append(text)
    return cleaned


def check_broker_id(broker_id: str) -> str:
    if not _ID_RE.match(broker_id):
        raise UnLeadError("Broker id must be a short slug.")
    return broker_id


def package_dir() -> Path:
    return Path(__file__).resolve().parent


def network_import_lines(text: str) -> list[str]:
    found = []
    for line in text.splitlines():
        stripped = line.strip()
        if not (stripped.startswith("import ") or stripped.startswith("from ")):
            continue
        for name in _NETWORK_IMPORTS:
            if name in stripped:
                found.append(stripped)
                break
    return found


def _scheme(secure: bool) -> str:
    # Split so this file is not a catalog of live URLs.
    return ("https" if secure else "http") + "://"


def scan_package_sources() -> list[str]:
    """Return human-readable hits. Empty means the package stays offline."""
    secure = _scheme(True)
    plain = _scheme(False)
    problems = []
    for path in sorted(package_dir().rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        for line in network_import_lines(text):
            problems.append(f"{path.name}: {line}")
        if path.name != "brokers.py" and (secure in text or plain in text):
            problems.append(f"{path.name}: contains a URL")
    return problems
