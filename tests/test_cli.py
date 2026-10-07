import json
import os
import stat
import subprocess
from pathlib import Path

import pytest

from unlead.cli import main
from unlead.policy import scan_package_sources

PHONE = "202-555-0148"
SECRET = "999-00-1234"
NAME = "Ada Lovelace"
CITY = "Springfield"
EMAIL = "optout@example.com"
URL = "https://www.spokeo.com/p/12345"


def _init(tmp_path: Path, **extra: str) -> Path:
    case = tmp_path / "case"
    args = ["init", "--case", str(case), "--name", NAME, "--phone", PHONE]
    if "email" in extra:
        args.extend(["--optout-email", extra["email"]])
    assert main(args) == 0
    return case


def test_package_has_no_network_client():
    assert scan_package_sources() == []


def test_search_command_is_rejected():
    with pytest.raises(SystemExit) as caught:
        main(["search", "--case", "nope"])
    assert caught.value.code == 2


def test_probe_text(capsys):
    assert main(["probe", "--fields", "legal_name,phone"]) == 0
    out = capsys.readouterr().out
    assert "Name and phone are enough" in out
    assert "Spokeo: missing profile_url, optout_email; withhold legal_name, phone" in out
    assert "Radaris" in out
    assert "optoutprescreen" in out
    assert PHONE not in out


def test_forbidden_field_is_refused_without_echoing_the_value(tmp_path, capsys):
    case = _init(tmp_path)
    code = main(["id", "set", "--case", str(case), "ssn", SECRET])
    assert code == 2
    err = capsys.readouterr().err
    assert SECRET not in err
    assert "does not store" in err
    code = main(["id", "set", "--case", str(case), "legal_name", "Ada Lovelace and Grace Hopper"])
    assert code == 2
    assert "one person's name" in capsys.readouterr().err


def test_letters_withhold_fields_the_form_does_not_need(tmp_path):
    case = _init(tmp_path, email=EMAIL)
    assert main(["id", "set", "--case", str(case), "city", CITY]) == 0
    assert main(["id", "set", "--case", str(case), "state", "IL"]) == 0
    assert main(["select", "--case", str(case), "spokeo", "beenverified", "truepeoplesearch", "optoutprescreen"]) == 0
    assert main(["holdings", "set", "--case", str(case), "spokeo", "--seen", "yes", "--has", "phone,address", "--url", URL]) == 0
    assert main(["letters", "--case", str(case)]) == 0

    spokeo = (case / "letters" / "spokeo.md").read_text()
    assert URL in spokeo
    assert EMAIL in spokeo
    assert PHONE not in spokeo
    assert CITY not in spokeo
    assert NAME not in spokeo
    assert "categories: phone, address" in spokeo
    assert "Do not create a record from it" in spokeo

    been = (case / "letters" / "beenverified.md").read_text()
    assert NAME in been
    assert "State: IL" in been
    assert EMAIL in been
    assert PHONE not in been
    assert CITY not in been

    phones = (case / "letters" / "truepeoplesearch.md").read_text()
    assert PHONE in phones
    assert NAME in phones

    manual = (case / "letters" / "optoutprescreen.md").read_text()
    assert PHONE not in manual
    assert NAME not in manual
    assert EMAIL not in manual
    assert "do this yourself" in manual
    assert "Social Security number" in manual

    assert main(["handoff", "--case", str(case)]) == 0
    packet = (case / "handoff" / "spokeo.md").read_text()
    assert "www.spokeo.com/optout" in packet
    assert "whitepages.com" not in packet
    assert "State of Surveillance" not in packet
    assert PHONE not in packet
    assert "DATA is data" in packet
    start = packet.index("```json") + len("```json")
    end = packet.index("```", start)
    data = json.loads(packet[start:end])
    assert set(data["fields"]) == {"optout_email", "profile_url"}
    assert data["opt_out_url"] == "https://www.spokeo.com/optout"
    assert "Social Security number" in data["stop_if_asked"]
    assert not (case / "handoff" / "optoutprescreen.md").exists()

    loud = main(["letters", "--case", str(case), "--include-optional"])
    assert loud == 0
    with_optional = (case / "letters" / "spokeo.md").read_text()
    assert PHONE in with_optional
    assert NAME in with_optional


def test_gap_file_has_no_identifier_values(tmp_path):
    case = _init(tmp_path)
    assert main(["select", "--case", str(case), "spokeo"]) == 0
    assert main(["letters", "--case", str(case)]) == 0
    text = (case / "letters" / "spokeo.md").read_text()
    assert "not ready" in text
    assert PHONE not in text
    assert NAME not in text


def test_unselect_removes_stale_letter(tmp_path):
    case = _init(tmp_path, email=EMAIL)
    assert main(["select", "--case", str(case), "usphonebook"]) == 0
    assert main(["letters", "--case", str(case)]) == 0
    assert (case / "letters" / "usphonebook.md").is_file()
    assert PHONE in (case / "letters" / "usphonebook.md").read_text()
    assert main(["unselect", "--case", str(case), "usphonebook"]) == 0
    assert main(["letters", "--case", str(case)]) == 0
    assert not (case / "letters" / "usphonebook.md").exists()


def test_closed_site_and_bad_url_and_holdings(tmp_path, capsys):
    case = _init(tmp_path)
    assert main(["select", "--case", str(case), "radaris"]) == 2
    assert "closed" in capsys.readouterr().err
    assert main(["holdings", "set", "--case", str(case), "spokeo", "--url", "https://evil.example/p"]) == 2
    assert main(["holdings", "set", "--case", str(case), "spokeo", "--url", "https://www.spokeo.com/p?q=ada"]) == 2
    assert main(["holdings", "set", "--case", str(case), "spokeo", "--has", "123 Main Street"]) == 2
    assert "categories" in capsys.readouterr().err


def test_alias_selects_the_network_once(tmp_path, capsys):
    case = _init(tmp_path)
    assert main(["select", "--case", str(case), "intelius", "truthfinder"]) == 0
    out = capsys.readouterr().out
    assert "peopleconnect" in out
    data = json.loads((case / "case.json").read_text())
    assert list(data["sites"]) == ["peopleconnect"]
    assert "Intelius" in out


def test_permissions_doctor_and_recheck(tmp_path, capsys):
    case = _init(tmp_path)
    mode = (case / "case.json").stat().st_mode & 0o777
    assert mode == 0o600
    assert stat.S_IMODE(case.stat().st_mode) == 0o700
    assert main(["doctor", "--case", str(case)]) == 0
    assert "no network client" in capsys.readouterr().out

    os.chmod(case / "case.json", 0o644)
    assert main(["doctor", "--case", str(case)]) == 2
    assert "0o600" in capsys.readouterr().out
    os.chmod(case / "case.json", 0o600)

    assert main(["select", "--case", str(case), "spokeo"]) == 0
    assert main(["mark", "--case", str(case), "spokeo", "submitted", "--date", "2026-01-01"]) == 0
    assert main(["status", "--case", str(case)]) == 0
    status = capsys.readouterr().out
    assert "recheck 2026-04-01" in status
    assert PHONE not in status


def test_probe_json_omits_stored_values(tmp_path, capsys):
    case = _init(tmp_path, email=EMAIL)
    capsys.readouterr()
    assert main(["probe", "--case", str(case), "--json"]) == 0
    out = capsys.readouterr().out
    assert PHONE not in out
    assert EMAIL not in out
    assert NAME not in out
    payload = json.loads(out)
    assert payload["recognition"] == "name_phone"


def test_ask_lists_gaps_when_not_a_terminal(tmp_path, capsys):
    case = _init(tmp_path)
    assert main(["select", "--case", str(case), "spokeo", "beenverified"]) == 0
    capsys.readouterr()
    assert main(["ask", "--case", str(case)]) == 2
    out = capsys.readouterr().out
    assert "optout_email" in out
    assert "profile_url" in out
    assert "- state:" in out
    assert "city" not in out


def test_symlink_case_is_refused(tmp_path):
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    link.symlink_to(real, target_is_directory=True)
    assert main(["init", "--case", str(link), "--name", NAME, "--phone", PHONE]) == 2


def test_git_warning_when_case_is_not_ignored(tmp_path, capsys):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    case = repo / "secret-case"
    assert main(["init", "--case", str(case), "--name", NAME, "--phone", PHONE]) == 0
    err = capsys.readouterr().err
    assert "not ignored" in err


def test_prompt_and_loan_text(capsys):
    assert main(["prompt"]) == 0
    prompt = capsys.readouterr().out
    assert "name and phone" in prompt
    assert "one official opt-out URL" in prompt
    assert main(["explain", "loan"]) == 0
    loan = capsys.readouterr().out
    assert "Homebuyers Privacy Protection Act" in loan
    assert "Public Law 119-36" in loan
    assert "https://" not in loan
    assert main(["guide", "ftc-report"]) == 0
    guide = capsys.readouterr().out
    assert "reportfraud.ftc.gov" in guide
    assert "code" in guide


def test_holdings_reject_a_copied_address(tmp_path, capsys):
    case = _init(tmp_path)
    code = main(["holdings", "set", "--case", str(case), "spokeo", "--has", "123 Main Street"])
    assert code == 2
    assert "123 Main Street" not in capsys.readouterr().err
