"""Command line for UnLead."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

from unlead import __version__
from unlead.catalog import catalog, catalog_meta, get_broker
from unlead.explain import TOPICS, WORKING_PROMPT
from unlead.handoff import write_handoff
from unlead.letters import render_manual, write_letters
from unlead.policy import (
    ALLOWED_FIELDS,
    FIELD_ORDER,
    FORBIDDEN_KEYS,
    UnLeadError,
    scan_package_sources,
)
from unlead.score import (
    field_plan,
    format_probe,
    questions_for,
    recognition,
    score_catalog,
    supplied_from_case,
)
from unlead.vault import (
    init_case,
    load_case,
    mark_site,
    mode_problem,
    recheck_on,
    save_case,
    select_site,
    set_holdings,
    set_identifier,
    unignored_warning,
    unselect_site,
    unset_identifier,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="unlead",
        description="UnLead — local opt-outs for your own people-search and data-broker listings.",
    )
    parser.add_argument("--version", action="version", version=f"UnLead {__version__}")
    sub = parser.add_subparsers(dest="cmd", required=True)

    init = sub.add_parser("init", help="Create a case for your own opt-out")
    _case(init, required=True)
    init.add_argument("--name")
    init.add_argument("--phone")
    init.add_argument("--optout-email")
    init.set_defaults(func=cmd_init)

    ident = sub.add_parser("id", help="Show or change stored fields")
    id_sub = ident.add_subparsers(dest="id_cmd", required=True)
    show = id_sub.add_parser("show")
    _case(show)
    show.set_defaults(func=cmd_id_show)
    setter = id_sub.add_parser("set")
    _case(setter)
    setter.add_argument("key")
    setter.add_argument("value")
    setter.set_defaults(func=cmd_id_set)
    unset = id_sub.add_parser("unset")
    _case(unset)
    unset.add_argument("key")
    unset.set_defaults(func=cmd_id_unset)

    probe = sub.add_parser("probe", help="Score fields against the catalog")
    _case(probe)
    probe.add_argument("--fields", help="Comma-separated field names, with no values")
    probe.add_argument("--json", action="store_true")
    probe.set_defaults(func=cmd_probe)

    sites = sub.add_parser("sites", help="List the catalog")
    sites.add_argument("site", nargs="?")
    sites.add_argument("--tier", type=int)
    sites.add_argument("--kind")
    sites.add_argument("--status")
    sites.set_defaults(func=cmd_sites)

    select = sub.add_parser("select", help="Choose sites to file")
    _case(select)
    select.add_argument("sites", nargs="*")
    select.add_argument("--tier", type=int)
    select.add_argument("--kind")
    select.set_defaults(func=cmd_select)

    unselect = sub.add_parser("unselect", help="Drop sites from the case")
    _case(unselect)
    unselect.add_argument("sites", nargs="+")
    unselect.set_defaults(func=cmd_unselect)

    holdings = sub.add_parser("holdings", help="Record categories you saw on your own listing")
    hold_sub = holdings.add_subparsers(dest="hold_cmd", required=True)
    hold_set = hold_sub.add_parser("set")
    _case(hold_set)
    hold_set.add_argument("site")
    hold_set.add_argument("--seen", choices=["yes", "no", "unconfirmed"])
    hold_set.add_argument("--has", help="Comma-separated categories")
    hold_set.add_argument("--url", help="https listing URL on that broker")
    hold_set.set_defaults(func=cmd_holdings)

    letters = sub.add_parser("letters", help="Write the opt-out for each selected site")
    _case(letters)
    letters.add_argument("--include-optional", action="store_true")
    letters.set_defaults(func=cmd_letters)

    handoff = sub.add_parser("handoff", help="Write one agent packet per ready site")
    _case(handoff)
    handoff.add_argument("--include-optional", action="store_true")
    handoff.set_defaults(func=cmd_handoff)

    ask = sub.add_parser("ask", help="Prompt for missing fields on selected sites")
    _case(ask)
    ask.set_defaults(func=cmd_ask)

    mark = sub.add_parser("mark", help="Record that you submitted or confirmed a site")
    _case(mark)
    mark.add_argument("site")
    mark.add_argument("state", choices=["draft", "submitted", "confirmed"])
    mark.add_argument("--date", help="YYYY-MM-DD, default today")
    mark.set_defaults(func=cmd_mark)

    status = sub.add_parser("status", help="Show the case")
    _case(status)
    status.set_defaults(func=cmd_status)

    doctor = sub.add_parser("doctor", help="Check the catalog, the package, and a case")
    _case(doctor)
    doctor.set_defaults(func=cmd_doctor)

    guide = sub.add_parser("guide", help="Show the manual steps for one site")
    guide.add_argument("site")
    guide.set_defaults(func=cmd_guide)

    explain = sub.add_parser("explain", help="Explain start, fields, agent, or loan")
    explain.add_argument("topic", choices=sorted(TOPICS))
    explain.set_defaults(func=cmd_explain)

    prompt = sub.add_parser("prompt", help="Print the working prompt")
    prompt.set_defaults(func=cmd_prompt)
    return parser


def _case(parser: argparse.ArgumentParser, required: bool = False) -> None:
    parser.add_argument("--case", required=required, help="Case directory")


def resolve_case(args: argparse.Namespace) -> Path:
    if getattr(args, "case", None):
        return Path(args.case)
    env = os.environ.get("UNLEAD_CASE")
    if env:
        return Path(env)
    default = Path("unlead-case")
    if (default / "case.json").is_file():
        return default
    raise UnLeadError("Pass --case DIR, or set UNLEAD_CASE.")


def _warn_case(directory: Path) -> None:
    for note in (mode_problem(directory), unignored_warning(directory)):
        if note:
            print(note, file=sys.stderr)


def cmd_init(args: argparse.Namespace) -> int:
    identifiers = {}
    if args.name:
        identifiers["legal_name"] = args.name
    if args.phone:
        identifiers["phone"] = args.phone
    if args.optout_email:
        identifiers["optout_email"] = args.optout_email
    if sys.stdin.isatty():
        identifiers = _prompt_missing_identity(identifiers)
    if "legal_name" not in identifiers or "phone" not in identifiers:
        raise UnLeadError("Pass --name and --phone, or run init in a terminal.")
    directory = Path(args.case)
    init_case(directory, identifiers)
    stored = ", ".join(key for key in FIELD_ORDER if key in identifiers)
    print(f"Case: {directory}")
    print(f"Subject: you. Stored fields: {stored}")
    _warn_case(directory)
    print("Next: unlead probe --case", directory)
    return 0


def _prompt_missing_identity(identifiers: dict) -> dict:
    if "legal_name" not in identifiers:
        print("Your legal name. Stored only in this case file.")
        identifiers["legal_name"] = input("> ").strip()
    if "phone" not in identifiers:
        print("One phone number. Stored only in this case file. It separates your row from someone with the same name.")
        identifiers["phone"] = input("> ").strip()
    if "optout_email" not in identifiers:
        print("Opt-out email. Optional. Press Enter to skip.")
        email = input("> ").strip()
        if email:
            identifiers["optout_email"] = email
    return identifiers


def cmd_id_show(args: argparse.Namespace) -> int:
    directory = resolve_case(args)
    case = load_case(directory)
    if not case["identifiers"]:
        print("No fields stored.")
        return 0
    for key in FIELD_ORDER:
        if key in case["identifiers"]:
            print(f"{key}: {case['identifiers'][key]}")
    return 0


def cmd_id_set(args: argparse.Namespace) -> int:
    directory = resolve_case(args)
    case = load_case(directory)
    set_identifier(case, args.key, args.value)
    save_case(directory, case)
    print(f"Stored {args.key}.")
    return 0


def cmd_id_unset(args: argparse.Namespace) -> int:
    directory = resolve_case(args)
    case = load_case(directory)
    unset_identifier(case, args.key)
    save_case(directory, case)
    print(f"Removed {args.key}.")
    return 0


def _parse_fields(text: str) -> set[str]:
    fields = set()
    for part in text.split(","):
        field = part.strip()
        if not field:
            continue
        if field in FORBIDDEN_KEYS:
            raise UnLeadError("That field is not part of the experiment.")
        if field not in ALLOWED_FIELDS:
            raise UnLeadError(f"Unknown field {field}.")
        fields.add(field)
    if not fields:
        raise UnLeadError("Pass at least one field name.")
    return fields


def cmd_probe(args: argparse.Namespace) -> int:
    assume = _parse_fields(args.fields) if args.fields else None
    case = None
    if assume is None:
        directory = resolve_case(args)
        case = load_case(directory)
        supplied = set(case["identifiers"])
    else:
        supplied = set(assume)
    rows = score_catalog(case=case, assume=assume)
    if args.json:
        level, _text = recognition(supplied)
        payload = {"recognition": level, "brokers": rows}
        print(json.dumps(payload, indent=2))
        return 0
    print(format_probe(rows, supplied), end="")
    return 0


def cmd_sites(args: argparse.Namespace) -> int:
    if args.site:
        broker, _alias = get_broker(args.site)
        print(_site_detail(broker))
        return 0
    for broker in catalog():
        if args.tier is not None and broker["tier"] != args.tier:
            continue
        if args.kind and broker["kind"] != args.kind:
            continue
        if args.status and broker["status"] != args.status:
            continue
        print(f"{broker['id']:28} {broker['status']:12} tier {broker['tier']:<2} {broker['name']}")
    return 0


def _site_detail(broker: dict) -> str:
    url = broker["opt_out_url"] or "do not open"
    lines = [
        f"{broker['name']} ({broker['id']})",
        f"  status: {broker['status']}  kind: {broker['kind']}  tier: {broker['tier']}",
        f"  opt-out: {url}",
        f"  requires: {', '.join(broker['form_requires']) or 'none'}",
        f"  matches with: {', '.join(broker['match_with']) or 'none'}",
        f"  optional, withheld unless you ask: {', '.join(broker['form_optional']) or 'none'}",
        f"  covers: {', '.join(broker['covers'])}",
        "  typical categories, not a finding about you: "
        + (", ".join(broker["typical_holdings"]) or "none"),
        f"  basis: {broker['basis']}",
    ]
    if broker["notes"]:
        lines.append(f"  notes: {broker['notes']}")
    if broker["hint"]:
        lines.append(f"  hint: {broker['hint']}")
    return "\n".join(lines)


def _brokers_for_select(args: argparse.Namespace) -> list[dict]:
    chosen = []
    seen = set()
    for token in args.sites:
        broker, via_alias = get_broker(token)
        if via_alias:
            print(f"{token} is {broker['name']} ({broker['id']}).")
        if broker["id"] not in seen:
            chosen.append(broker)
            seen.add(broker["id"])
    if args.tier is not None or args.kind:
        for broker in catalog():
            if broker["status"] != "open":
                continue
            if args.tier is not None and broker["tier"] != args.tier:
                continue
            if args.kind and broker["kind"] != args.kind:
                continue
            if broker["id"] not in seen:
                chosen.append(broker)
                seen.add(broker["id"])
    if not chosen:
        raise UnLeadError("Name a site, or pass --tier or --kind.")
    return chosen


def cmd_select(args: argparse.Namespace) -> int:
    directory = resolve_case(args)
    case = load_case(directory)
    for broker in _brokers_for_select(args):
        already = select_site(case, broker)
        if already:
            print(f"Already selected {broker['id']}.")
            continue
        print(f"Selected {broker['id']}.")
        if len(broker["covers"]) > 1:
            print(f"  Covers: {', '.join(broker['covers'])}. File this once.")
    save_case(directory, case)
    return 0


def cmd_unselect(args: argparse.Namespace) -> int:
    directory = resolve_case(args)
    case = load_case(directory)
    for token in args.sites:
        broker, _alias = get_broker(token)
        unselect_site(case, broker["id"])
        print(f"Unselected {broker['id']}.")
    save_case(directory, case)
    return 0


def cmd_holdings(args: argparse.Namespace) -> int:
    directory = resolve_case(args)
    case = load_case(directory)
    broker, _alias = get_broker(args.site)
    categories = None
    if args.has is not None:
        categories = [part.strip() for part in args.has.split(",") if part.strip()]
    set_holdings(case, broker, seen=args.seen, holdings=categories, url=args.url)
    save_case(directory, case)
    print(f"Recorded holdings for {broker['id']}.")
    return 0


def cmd_letters(args: argparse.Namespace) -> int:
    directory = resolve_case(args)
    case = load_case(directory)
    written = write_letters(directory, case, include_optional=args.include_optional)
    print(f"Wrote {len(written)} file(s) in {directory / 'letters'}.")
    return 0


def cmd_handoff(args: argparse.Namespace) -> int:
    directory = resolve_case(args)
    case = load_case(directory)
    written = write_handoff(directory, case, include_optional=args.include_optional)
    print(f"Wrote {len(written)} agent packet(s) in {directory / 'handoff'}.")
    print("Paste one packet into your browser agent. Finish that site before the next packet.")
    return 0


def cmd_ask(args: argparse.Namespace) -> int:
    directory = resolve_case(args)
    case = load_case(directory)
    questions = questions_for(case)
    if not questions:
        print("Nothing to add. Selected open sites have the fields their forms require.")
        return 0
    if not sys.stdin.isatty():
        print("These fields are still required. Run `unlead ask` in a terminal, or use `unlead id set`.")
        for question in questions:
            names = ", ".join(question.brokers)
            print(f"- {question.field}: {names}")
        return 2
    for question in questions:
        print(question.prompt)
        print("Needed by: " + ", ".join(question.brokers))
        while True:
            answer = input("> ").strip()
            if not answer:
                print(f"Skipped {question.field}.")
                break
            try:
                if question.broker_id:
                    broker, _alias = get_broker(question.broker_id)
                    set_holdings(case, broker, url=answer)
                else:
                    set_identifier(case, question.field, answer)
            except UnLeadError as exc:
                print(str(exc))
                continue
            save_case(directory, case)
            print(f"Stored {question.field}.")
            break
    return 0


def cmd_mark(args: argparse.Namespace) -> int:
    directory = resolve_case(args)
    case = load_case(directory)
    broker, _alias = get_broker(args.site)
    day = args.date or date.today().isoformat()
    mark_site(case, broker, args.state, day)
    save_case(directory, case)
    print(f"Marked {broker['id']} {args.state}.")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    directory = resolve_case(args)
    case = load_case(directory)
    stored = [key for key in FIELD_ORDER if key in case["identifiers"]]
    print(f"Case directory: {directory}")
    print("Subject: you")
    print("Stored fields: " + (", ".join(stored) or "none"))
    _warn_case(directory)
    rows = []
    for broker_id, record in case.get("sites", {}).items():
        if record.get("selected"):
            rows.append((get_broker(broker_id)[0], record))
    rows.sort(key=lambda pair: (pair[0]["tier"], pair[0]["name"].casefold()))
    print(f"Selected: {len(rows)}")
    for broker, record in rows:
        plan = field_plan(broker, supplied_from_case(case, broker["id"]))
        if broker["status"] == "human_only":
            state = "manual"
        elif broker["status"] == "closed":
            state = "closed"
        elif plan["agent_ready"]:
            state = "agent-ready"
        else:
            state = "missing " + ", ".join(plan["missing"])
        extra = ""
        if record.get("status") and record["status"] != "draft":
            extra = f"  marked {record['status']} {record.get('submitted_on', '')}".rstrip()
        due = recheck_on(record, broker)
        if due:
            extra += f"  recheck {due}"
        seen = record.get("seen") or "unconfirmed"
        print(f"  {broker['id']:28} {state}  seen {seen}{extra}")
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    meta = catalog_meta()
    print(f"Catalog revised {meta['revised']}. {meta['count']} entries.")
    counts = meta["counts"]
    print(
        "  open {open}  human_only {human_only}  closed {closed}".format(
            open=counts.get("open", 0),
            human_only=counts.get("human_only", 0),
            closed=counts.get("closed", 0),
        )
    )
    problems = scan_package_sources()
    exit_code = 0
    if problems:
        exit_code = 2
        print("Package scan:")
        for problem in problems:
            print(f"  {problem}")
    else:
        print("Package scan: no network client, no stray URLs.")
    if args.case:
        directory = Path(args.case)
        load_case(directory)
        note = mode_problem(directory)
        if note:
            print(note)
            exit_code = 2
        else:
            print("Case file mode 0600 and directory mode 0700.")
        warning = unignored_warning(directory)
        if warning:
            print(warning)
    return exit_code


def cmd_guide(args: argparse.Namespace) -> int:
    broker, _alias = get_broker(args.site)
    if broker["status"] == "closed":
        print(_site_detail(broker))
        print("Do not open the old domain and do not type your information into it.")
        return 0
    if broker["status"] == "human_only":
        print(render_manual(broker), end="")
        return 0
    print(_site_detail(broker))
    print("An agent packet is written once the required fields are in the case.")
    return 0


def cmd_explain(args: argparse.Namespace) -> int:
    print(TOPICS[args.topic])
    return 0


def cmd_prompt(args: argparse.Namespace) -> int:
    print(WORKING_PROMPT)
    return 0


def main(argv: list[str] | None = None) -> int:
    try:
        args = _parser().parse_args(argv)
        return args.func(args)
    except UnLeadError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
