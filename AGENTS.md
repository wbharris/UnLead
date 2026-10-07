# UnLead

Local opt-out case for the operator's own listings. Catalog and letters only.

- Do not add an HTTP client, a scraper, a people-search call, a CAPTCHA solver, or a browser driver. `unlead.policy.scan_package_sources` fails the tests if one appears.
- Do not add case fields for a Social Security number, a date of birth, a government ID, a password, a payment card, or a biometric.
- Opt-out URLs live in `src/unlead/brokers.py`. A hint copied into an agent packet must not contain a URL. Closed brokers have no URL.
- Agent packets stay one site, and they send only `form_requires` ∪ `match_with` unless the user passed `--include-optional`.
- Case files are mode 0600 under a 0700 directory and are gitignored when created as `unlead-case/` or `cases/`. Do not commit a case.
- Tests: `PYTHONPATH=src python3 -m pytest -q` from this repo. The repo root is `/home/iceroot/Projects/unlead`, not `/home/iceroot/Projects`.
