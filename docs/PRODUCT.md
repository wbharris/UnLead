# UnLead product notes

UnLead prepares opt-out requests for the person operating it. The case file stays on that computer. A browser agent, if the person uses one, receives one site at a time and only the fields that site's published form needs.

## Minimum fields

The starting pair is legal name and one phone number.

That pair is for recognition. On a typical people-search page the phone is what separates you from other people who share your name. A name alone collides. A phone alone can single out a reverse-lookup row, and the name is still what you use to reject a row that is not yours.

Submission is a second, smaller set. For each broker the catalog stores:

- `form_requires` — the form does not finish without these
- `match_with` — the form uses these to find the existing row
- `form_optional` — the form offers these, and UnLead withholds them unless you pass `--include-optional`

The letter and the agent packet send the intersection of what you stored and `form_requires` ∪ `match_with`. A stored city stays in the case and out of a Spokeo request, because Spokeo matches on the listing URL. The same phone is sent to USPhoneBook, because that form matches on the phone.

`unlead probe` prints both results. `unlead ask` prompts only for required fields the selected open sites still lack.

## What a listing contains

UnLead does not know what a site holds about you. Typical categories on a catalog entry are labeled as typical, not as a finding. After you look at your own row, `unlead holdings set` records categories: name, phone, email, address, relatives, age, employer, photo. A street address or a relative's name is rejected. The letter says which categories you saw, or that you have not confirmed a listing, and it tells the broker to discard the request if nothing matches rather than create a record from it.

## Agent packets

`unlead handoff` writes `handoff/<id>.md` for each selected open site whose required fields are filled. The JSON block marked DATA is the only fields the agent may type. The rules tell it to stop for a CAPTCHA, a phone call, an SMS code, a payment, a password, or any ask for a Social Security number, a date of birth, a government ID, or a face photo. You open confirmation email yourself. You paste one file per session.

Human-only entries never get a packet. That set includes OptOutPrescreen, the credit-bureau marketing pages, LexisNexis, California DROP, PimEyes, FaceCheck, Google results about you, the FTC report, and SpyDialer (the removal control is a footer on a search homepage, and there is no stable deep link to hand an agent).

## After a loan

Three piles:

1. People-search and marketing brokers. Tier 1 in the catalog is the first pass. PeopleConnect is one filing for Intelius, TruthFinder, Instant Checkmate, and US Search. BeenVerified is a separate filing for BeenVerified, PeopleLooker, NeighborWho, and Ownerly.
2. Prescreened firm offers. The Homebuyers Privacy Protection Act, Public Law 119-36, signed September 5, 2025, limits residential-mortgage trigger leads starting in March 2026. Other loans can still become firm offers. OptOutPrescreen is the official five-year or permanent opt-out and it asks for a Social Security number and a date of birth. A GAO review dated October 6, 2026 says it is too early to measure the mortgage rule.
3. Scam calls. The Do Not Call Registry binds lawful telemarketers. A caller asking for a code or a fee is an FTC report, which you file yourself.

This is operational detail for those three official paths. It is not legal advice.

## Catalog maintenance

URLs move, and a dead domain gets parked by someone new. When you update an entry, take the URL from that site's own footer, put the date and the reason in `basis`, and keep `allowed_hosts` to the opt-out host. Do not add the marketing search host when it is a different host. Hints must not contain a URL, because hints are copied into the agent packet. Closed sites have `opt_out_url` set to null.

`unlead doctor` checks that the package still has no HTTP client and that a case file is mode 0600 in a directory mode 0700.

## Out of scope

Looking up a person other than the operator. Fetching broker pages. Solving a CAPTCHA. Storing a Social Security number, a date of birth, a government ID, a password, or a biometric. Filing an FTC report or an OptOutPrescreen request from an agent. Claiming a site has a specific record before you have looked.
