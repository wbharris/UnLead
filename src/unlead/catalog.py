"""Load and check the opt-out catalog."""

from __future__ import annotations

from urllib.parse import urlsplit

from unlead.brokers import BROKERS, CATALOG_BASIS, CATALOG_COUNT, CATALOG_REVISED
from unlead.policy import ALLOWED_FIELDS, HOLDING_CATEGORIES, UnLeadError, check_broker_id, host_allowed

_STATUSES = {"open", "human_only", "closed"}
_KINDS = {"people_search", "marketing", "registry", "biometric", "search_engine"}
_FLOWS = {"form", "optout_lookup", "none"}
_REQUIRED_NEVER = {"ssn", "government_id", "date_of_birth", "password", "biometric", "payment_card"}


def _https_host(url: str, broker_id: str) -> str:
    parts = urlsplit(url)
    if parts.scheme != "https" or not parts.hostname:
        raise UnLeadError(f"{broker_id}: opt-out URL must be https.")
    if parts.username or parts.password or parts.query or parts.fragment:
        raise UnLeadError(f"{broker_id}: opt-out URL must not carry a query, fragment, or login.")
    return parts.hostname


def validate_broker(raw: dict) -> dict:
    broker = dict(raw)
    broker_id = broker.get("id", "")
    if not isinstance(broker_id, str) or not broker_id:
        raise UnLeadError("Broker is missing an id.")
    check_broker_id(broker_id)
    status = broker.get("status")
    if status not in _STATUSES:
        raise UnLeadError(f"{broker_id}: bad status.")
    if broker.get("kind") not in _KINDS:
        raise UnLeadError(f"{broker_id}: bad kind.")
    if broker.get("flow") not in _FLOWS:
        raise UnLeadError(f"{broker_id}: bad flow.")
    requires = list(broker.get("form_requires") or [])
    match = list(broker.get("match_with") or [])
    optional = list(broker.get("form_optional") or [])
    for field in requires + match + optional:
        if field not in ALLOWED_FIELDS:
            raise UnLeadError(f"{broker_id}: field {field} is not on the allowlist.")
    if set(requires) & set(optional):
        raise UnLeadError(f"{broker_id}: a field is both required and optional.")
    never = set(broker.get("never_send") or [])
    if not _REQUIRED_NEVER <= never:
        raise UnLeadError(f"{broker_id}: never_send is missing a required secret.")
    for category in broker.get("typical_holdings") or []:
        if category not in HOLDING_CATEGORIES:
            raise UnLeadError(f"{broker_id}: unknown holding category {category}.")
    hint = broker.get("hint") or ""
    if ("http" + "://") in hint or ("https" + "://") in hint:
        raise UnLeadError(f"{broker_id}: hint must not contain a URL.")
    hosts = list(broker.get("allowed_hosts") or [])
    url = broker.get("opt_out_url")
    if status == "closed":
        if url or hosts or broker.get("agent_allowed") or requires:
            raise UnLeadError(f"{broker_id}: a closed site has no URL and no agent packet.")
    else:
        if not url:
            raise UnLeadError(f"{broker_id}: missing opt-out URL.")
        host = _https_host(url, broker_id)
        if not host_allowed(host, hosts):
            raise UnLeadError(f"{broker_id}: opt-out host is not in allowed_hosts.")
        if status == "open" and not requires:
            raise UnLeadError(f"{broker_id}: an open site needs at least one required field.")
        if status == "human_only" and broker.get("agent_allowed"):
            raise UnLeadError(f"{broker_id}: human-only sites are not handed to an agent.")
        if status == "open" and not broker.get("agent_allowed"):
            raise UnLeadError(f"{broker_id}: open sites are agent-ready once their fields are filled.")
    if status == "closed" and broker.get("flow") != "none":
        raise UnLeadError(f"{broker_id}: closed flow must be none.")
    return broker


def load_catalog() -> list[dict]:
    brokers = []
    seen = set()
    aliases: dict[str, str] = {}
    for raw in BROKERS:
        broker = validate_broker(raw)
        broker_id = broker["id"]
        if broker_id in seen:
            raise UnLeadError(f"Duplicate broker id {broker_id}.")
        seen.add(broker_id)
        keys = {broker_id, broker["name"].casefold()}
        for alias in broker.get("aliases") or []:
            keys.add(alias.casefold())
        for key in keys:
            if key in aliases and aliases[key] != broker_id:
                raise UnLeadError(f"Alias {key} is used twice.")
            aliases[key] = broker_id
        brokers.append(broker)
    if len(brokers) != CATALOG_COUNT:
        raise UnLeadError(f"Catalog count is {len(brokers)}, expected {CATALOG_COUNT}.")
    return brokers


_CACHE: list[dict] | None = None
_ALIASES: dict[str, str] | None = None


def catalog() -> list[dict]:
    global _CACHE, _ALIASES
    if _CACHE is None:
        _CACHE = load_catalog()
        _ALIASES = {}
        for broker in _CACHE:
            _ALIASES[broker["id"]] = broker["id"]
            _ALIASES[broker["name"].casefold()] = broker["id"]
            for alias in broker.get("aliases") or []:
                _ALIASES[alias.casefold()] = broker["id"]
    return _CACHE


def alias_map() -> dict[str, str]:
    catalog()
    assert _ALIASES is not None
    return _ALIASES


def get_broker(token: str) -> tuple[dict, bool]:
    """Return the broker and whether `token` was an alias rather than the id."""
    key = token.strip().casefold()
    broker_id = alias_map().get(key)
    if broker_id is None:
        raise UnLeadError(f"Unknown site {token}. Run `unlead sites`.")
    for broker in catalog():
        if broker["id"] == broker_id:
            return broker, key != broker_id and key != broker["name"].casefold()
    raise UnLeadError(f"Unknown site {token}.")


def by_id(broker_id: str) -> dict:
    for broker in catalog():
        if broker["id"] == broker_id:
            return broker
    raise UnLeadError(f"Unknown site {broker_id}.")


def catalog_meta() -> dict:
    rows = catalog()
    counts: dict[str, int] = {}
    for broker in rows:
        counts[broker["status"]] = counts.get(broker["status"], 0) + 1
    return {
        "revised": CATALOG_REVISED,
        "basis": CATALOG_BASIS,
        "count": len(rows),
        "counts": counts,
    }
