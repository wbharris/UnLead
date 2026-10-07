# Unlead

Unlead is a local opt-out case for your own people-search and data-broker listings. You store a name and a phone number on this computer. Unlead scores every site in its catalog against those fields, writes the opt-out each selected site actually requires, and writes one packet per site for a browser agent you already use.

A loan application can feed three different kinds of calls. People-search sites already publish a name, a phone, and an address. Credit bureaus sell prescreened firm offers, with a mortgage-specific limit that started in March 2026. Scam callers are neither of those. `unlead explain loan` separates the three.

## Install

```bash
cd /home/iceroot/Projects/unlead
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/unlead --version
```

Python 3.11 or newer. The runtime has no third-party dependencies. `PYTHONPATH=src` works without an install:

```bash
PYTHONPATH=src python3 -m unlead --version
```

## Working prompt

`unlead prompt` prints this:

> Score each broker in the Unlead catalog against the name and phone stored in this local case. Say which of those fields each opt-out form actually needs, and which fields the case will withhold. For the sites I select, record only the categories I confirm I saw on my own listing. Write the exact opt-out for each selected site, then write one agent packet per site that is ready. I will paste a single packet into a browser agent I already use. That agent opens one official opt-out URL and enters only the packet's fields.

## Use

```bash
unlead init --case ~/unlead-case --name "Your Name" --phone "202-555-0148"
unlead probe --case ~/unlead-case
unlead select --tier 1 --case ~/unlead-case
unlead ask --case ~/unlead-case
unlead holdings set spokeo --seen yes --has phone,address \
  --url "https://www.spokeo.com/your-listing" --case ~/unlead-case
unlead letters --case ~/unlead-case
unlead handoff --case ~/unlead-case
```

`init` and `ask` prompt in a terminal when you leave a field off the command. Press Enter to skip a field. A skipped field leaves the sites that require it unready.

`probe --fields legal_name,phone` runs the minimum-field experiment with no case and no values. Name plus phone is enough to tell your row from someone who shares your name. It is often not what the opt-out form wants. Spokeo wants the listing URL and an email, so the default letter withholds the phone. A reverse-phone site sends the phone and withholds the name.

Paste one file from `handoff/` into Grok, a GPT agent, Muse, or another browser agent. Finish that site, including any CAPTCHA or confirmation email yourself, then paste the next file. `unlead mark spokeo submitted --case ~/unlead-case` starts the recheck clock. Listings come back.

These stay manual, and the guide files contain none of your identifiers:

```bash
unlead guide optoutprescreen
unlead guide donotcall
unlead guide ftc-report
unlead guide drop
```

OptOutPrescreen asks for a Social Security number and a date of birth. File that one in your own browser. Unlead will not store those and will not put them in a packet.

## What the case holds

The case directory is mode `0700` and `case.json` is mode `0600`. Fields are your name, one phone, an opt-out email, city, state, and postal code, plus a listing URL and category checklist per site. Holdings are categories (`phone`, `address`, `relatives`), not a copy of the page.

`probe` and `status` print field names. `id show`, the letter, and the agent packet contain the values you chose to send to that one site.

Keep the case out of git. `unlead status` warns when the directory sits in a repo that would commit it.

## Catalog

`src/unlead/brokers.py` is the catalog, revised 2026-10-07. People-search URLs follow the State of Surveillance master list link check of 2026-09-28, with a note on the entry when a 2026 guide disagreed (MyLife and FastPeopleSearch). Closed sites (Radaris, PeekYou, Nuwber, and others from that check) have no URL. Confirm the footer link on the live site before you type. A parked domain is a new collector.

## Tests

```bash
PYTHONPATH=src python3 -m pytest -q
```

## License

GPL-3.0-or-later. See `LICENSE`.
