"""Opt-out catalog. Official removal pages only. No people-search endpoints.

URLs for people-search sites follow the State of Surveillance master list
link check of 2026-09-28, except where a 2026 guide disagreed. Those
disagreements are on the entry. Confirm the footer link on the site itself
before typing. A parked domain is a new place to collect data, which is why
closed entries have no URL.
"""

from __future__ import annotations

CATALOG_REVISED = "2026-10-07"
CATALOG_COUNT = 52

CATALOG_BASIS = (
    "People-search opt-out URL from the State of Surveillance master list, "
    "link-checked by that site on 2026-09-28."
)

OFFICIAL_LINKS = {
    "ftc_report": "https://reportfraud.ftc.gov/",
}

NEVER = [
    "ssn",
    "government_id",
    "date_of_birth",
    "password",
    "biometric",
    "payment_card",
]

PEOPLE = ["name", "phone", "address", "relatives", "age"]


def entry(**kwargs) -> dict:
    row = {
        "form_optional": [],
        "covers": [],
        "typical_holdings": list(PEOPLE),
        "stop_if_asked": [],
        "account_required": False,
        "agent_allowed": True,
        "recheck_days": 90,
        "verification": "email",
        "processing": "Often a few days. The site's own page is the clock that counts.",
        "method": "web form",
        "flow": "form",
        "notes": "",
        "basis": CATALOG_BASIS,
        "aliases": [],
        "hint": "",
        "never_send": list(NEVER),
        "tier": 2,
        "kind": "people_search",
        "status": "open",
    }
    row.update(kwargs)
    if not row["covers"]:
        row["covers"] = [row["name"]]
    return row


def closed(broker_id: str, name: str, notes: str) -> dict:
    return entry(
        id=broker_id,
        name=name,
        status="closed",
        agent_allowed=False,
        opt_out_url=None,
        allowed_hosts=[],
        form_requires=[],
        match_with=[],
        form_optional=[],
        typical_holdings=[],
        recheck_days=0,
        tier=9,
        flow="none",
        method="none",
        verification="none",
        processing="",
        notes=notes,
        basis=CATALOG_BASIS,
    )


def manual(**kwargs) -> dict:
    kwargs["status"] = "human_only"
    kwargs["agent_allowed"] = False
    return entry(**kwargs)


_CLOSED = (
    "As of the 2026-09-28 master-list check this site no longer ran a people search. "
    "Do not type your information into the old domain."
)

BROKERS = [
    entry(
        id="beenverified",
        name="BeenVerified",
        tier=1,
        opt_out_url="https://www.beenverified.com/app/optout/search",
        allowed_hosts=["beenverified.com"],
        flow="optout_lookup",
        form_requires=["legal_name", "state", "optout_email"],
        match_with=["legal_name", "state"],
        form_optional=["phone"],
        verification="email",
        processing="Often 24 to 72 hours.",
        covers=["BeenVerified", "PeopleLooker", "NeighborWho", "Ownerly"],
        aliases=["been verified", "peoplelooker", "neighborwho", "ownerly"],
        hint=(
            "One filing is for this network. It does not cover the PeopleConnect "
            "suppression center. Do not open a paid report."
        ),
        notes=(
            "File PeopleConnect separately for Intelius, TruthFinder, Instant Checkmate, "
            "and US Search. Some 2026 guides mention the path /f/optout/search. "
            "If the /app/ page does not load, use the footer opt-out on beenverified.com."
        ),
        basis=(
            "Opt-out URL on the 2026-09-28 master list. Sirveil's July 2026 guide describes "
            "the same BeenVerified network and a different PeopleConnect network."
        ),
    ),
    entry(
        id="spokeo",
        name="Spokeo",
        tier=1,
        opt_out_url="https://www.spokeo.com/optout",
        allowed_hosts=["spokeo.com"],
        form_requires=["profile_url", "optout_email"],
        match_with=["profile_url"],
        form_optional=["legal_name", "phone", "city", "state"],
        processing="Often 24 to 48 hours.",
        hint="Paste the listing URL. Do not use the Spokeo search box.",
        notes="The listing URL is the match. Name and phone can stay in the case and out of this request.",
    ),
    entry(
        id="whitepages",
        name="Whitepages",
        tier=1,
        opt_out_url="https://www.whitepages.com/suppression-requests",
        allowed_hosts=["whitepages.com"],
        form_requires=["profile_url", "phone"],
        match_with=["profile_url", "phone"],
        form_optional=["optout_email", "legal_name"],
        verification="phone call",
        processing="Often about 24 hours after the verification call.",
        aliases=["white pages"],
        hint=(
            "Use the phone already on the listing. When the page starts a verification call, "
            "stop and let the human take it. Do not type a new phone number."
        ),
    ),
    entry(
        id="peopleconnect",
        name="PeopleConnect",
        tier=1,
        opt_out_url="https://suppression.peopleconnect.us/login",
        allowed_hosts=["suppression.peopleconnect.us"],
        form_requires=["legal_name", "optout_email"],
        match_with=["legal_name"],
        form_optional=["state", "phone"],
        account_required=True,
        processing="Often about 72 hours.",
        covers=["Intelius", "TruthFinder", "Instant Checkmate", "US Search"],
        aliases=["intelius", "truthfinder", "instant checkmate", "instantcheckmate", "us search", "ussearch"],
        hint=(
            "If the page asks for an account, stop and let the human set the password. "
            "Do not invent one. One filing covers this network. Do not repeat it on each brand."
        ),
        notes=(
            "Brand lists change. Read the suppression page for the current list and stop there. "
            "Do not also type the same identifiers into each brand's marketing site."
        ),
        basis="Suppression center URL on the 2026-09-28 master list.",
    ),
    entry(
        id="peoplefinders",
        name="PeopleFinders",
        tier=1,
        opt_out_url="https://www.peoplefinders.com/opt-out",
        allowed_hosts=["peoplefinders.com"],
        form_requires=["legal_name", "optout_email"],
        match_with=["legal_name"],
        form_optional=["phone", "state", "city"],
        processing="Often 3 to 9 days.",
        aliases=["people finders"],
    ),
    entry(
        id="mylife",
        name="MyLife",
        tier=1,
        opt_out_url="https://www.mylife.com/privacyrequest",
        allowed_hosts=["mylife.com"],
        form_requires=["profile_url", "optout_email"],
        match_with=["profile_url"],
        form_optional=["legal_name", "city", "state", "postal_code"],
        processing="Often up to 15 days.",
        aliases=["my life"],
        hint="Paste the listing URL. Leave city, state, and postal code blank unless you add them on purpose.",
        notes="A mail fallback published by guides is privacy@mylife.com. Prefer the form.",
        basis=(
            "Incogni's MyLife guide, current in 2026, says /ccpa/index.pubview returns 404 and "
            "points to /privacyrequest. The 2026-09-28 master list still shows the older path. "
            "Confirm the privacy link in the MyLife footer."
        ),
    ),
    entry(
        id="fastpeoplesearch",
        name="FastPeopleSearch",
        tier=1,
        opt_out_url="https://www.fastpeoplesearch.com/optout",
        allowed_hosts=["fastpeoplesearch.com"],
        form_requires=["legal_name", "optout_email"],
        match_with=["legal_name"],
        form_optional=["phone"],
        processing="The site asks you to allow about 3 days. The emailed form link expires in about a day.",
        aliases=["fast people search", "fastpeoplesearch"],
        hint="Let the human open the confirmation email the same day. The link expires quickly.",
        basis=(
            "Encovert's guide dated 2026-10-05 says the form is at /optout and starts with name plus email. "
            "The 2026-09-28 master list shows /removal. Unlead uses /optout."
        ),
    ),
    entry(
        id="truepeoplesearch",
        name="TruePeopleSearch",
        tier=1,
        opt_out_url="https://www.truepeoplesearch.com/removal",
        allowed_hosts=["truepeoplesearch.com"],
        form_requires=["legal_name", "phone", "optout_email"],
        match_with=["legal_name", "phone"],
        processing="Varies. Guides say the emailed link expires in about a day.",
        aliases=["true people search"],
        hint="Let the human open the confirmation email the same day.",
    ),
    entry(
        id="thatsthem",
        name="That'sThem",
        tier=1,
        opt_out_url="https://thatsthem.com/optout",
        allowed_hosts=["thatsthem.com"],
        form_requires=["legal_name", "phone", "optout_email"],
        match_with=["legal_name", "phone"],
        aliases=["thats them", "that's them"],
        notes="Guides describe listings that can include email and IP data. The request still sends only the allowlist.",
    ),
    entry(
        id="usphonebook",
        name="USPhoneBook",
        tier=1,
        opt_out_url="https://www.usphonebook.com/opt-out",
        allowed_hosts=["usphonebook.com"],
        form_requires=["phone", "optout_email"],
        match_with=["phone"],
        form_optional=["legal_name"],
        aliases=["us phonebook", "usphone book"],
        hint="This one matches on the phone number. Do not add a second number.",
    ),
    entry(
        id="cyberbackgroundchecks",
        name="CyberBackgroundChecks",
        tier=2,
        opt_out_url="https://www.cyberbackgroundchecks.com/removal",
        allowed_hosts=["cyberbackgroundchecks.com"],
        flow="optout_lookup",
        form_requires=["legal_name", "state", "optout_email"],
        match_with=["legal_name", "state"],
        form_optional=["phone"],
        aliases=["cyber background checks"],
    ),
    entry(
        id="checkpeople",
        name="CheckPeople",
        tier=2,
        opt_out_url="https://checkpeople.com/opt-out",
        allowed_hosts=["checkpeople.com"],
        form_requires=["legal_name", "optout_email"],
        match_with=["legal_name"],
        form_optional=["phone", "state"],
        aliases=["check people"],
    ),
    entry(
        id="advancedbackgroundchecks",
        name="AdvancedBackgroundChecks",
        tier=2,
        opt_out_url="https://www.advancedbackgroundchecks.com/removal",
        allowed_hosts=["advancedbackgroundchecks.com"],
        flow="optout_lookup",
        form_requires=["legal_name", "state", "optout_email"],
        match_with=["legal_name", "state"],
        form_optional=["phone"],
        aliases=["advanced background checks"],
    ),
    entry(
        id="smartbackgroundchecks",
        name="SmartBackgroundChecks",
        tier=2,
        opt_out_url="https://www.smartbackgroundchecks.com/optout",
        allowed_hosts=["smartbackgroundchecks.com"],
        form_requires=["legal_name", "optout_email"],
        match_with=["legal_name"],
        form_optional=["phone", "state"],
        aliases=["smart background checks"],
        notes="File PeopleFinders on its own. A guide that says one removal covers the other goes stale.",
    ),
    entry(
        id="searchpeoplefree",
        name="SearchPeopleFree",
        tier=2,
        opt_out_url="https://www.searchpeoplefree.com/opt-out",
        allowed_hosts=["searchpeoplefree.com"],
        form_requires=["legal_name", "optout_email"],
        match_with=["legal_name"],
        form_optional=["phone", "city", "state"],
        aliases=["search people free"],
    ),
    entry(
        id="usa-people-search",
        name="USA-People-Search",
        tier=2,
        opt_out_url="https://www.usa-people-search.com/removal",
        allowed_hosts=["usa-people-search.com"],
        flow="optout_lookup",
        form_requires=["legal_name", "state", "optout_email"],
        match_with=["legal_name", "state"],
        form_optional=["phone"],
        aliases=["usa people search"],
    ),
    entry(
        id="peoplesearchnow",
        name="PeopleSearchNow",
        tier=2,
        opt_out_url="https://www.peoplesearchnow.com/opt-out",
        allowed_hosts=["peoplesearchnow.com"],
        flow="optout_lookup",
        form_requires=["legal_name", "state", "optout_email"],
        match_with=["legal_name", "state"],
        form_optional=["phone"],
        aliases=["people search now"],
    ),
    entry(
        id="privateeye",
        name="PrivateEye",
        tier=2,
        opt_out_url="https://www.privateeye.com/removal",
        allowed_hosts=["privateeye.com"],
        form_requires=["legal_name", "optout_email"],
        match_with=["legal_name"],
        form_optional=["phone", "state"],
        aliases=["private eye"],
        notes="Guides say the site emails a removal form. Let the human open that mail.",
    ),
    entry(
        id="privaterecords",
        name="PrivateRecords",
        tier=2,
        opt_out_url="https://www.privaterecords.net/optOut/name/landing",
        allowed_hosts=["privaterecords.net"],
        flow="optout_lookup",
        form_requires=["legal_name", "state", "optout_email"],
        match_with=["legal_name", "state"],
        form_optional=["phone"],
        aliases=["private records"],
    ),
    entry(
        id="searchquarry",
        name="SearchQuarry",
        tier=2,
        opt_out_url="https://members.searchquarry.com/removeMyData/",
        allowed_hosts=["members.searchquarry.com"],
        form_requires=["legal_name", "optout_email"],
        match_with=["legal_name"],
        form_optional=["phone", "state"],
        account_required=True,
        aliases=["search quarry"],
        hint=(
            "Stay on members.searchquarry.com. If it asks for an account, stop and let the human "
            "set the password. Do not open a different SearchQuarry host."
        ),
    ),
    entry(
        id="veripages",
        name="Veripages",
        tier=2,
        opt_out_url="https://veripages.com/inner/control-privacy",
        allowed_hosts=["veripages.com"],
        form_requires=["legal_name", "optout_email"],
        match_with=["legal_name"],
        form_optional=["phone", "city", "state"],
    ),
    entry(
        id="unmask",
        name="UnMask",
        tier=2,
        opt_out_url="https://unmask.com/opt-out/",
        allowed_hosts=["unmask.com"],
        form_requires=["legal_name", "optout_email"],
        match_with=["legal_name"],
        form_optional=["phone", "state"],
        aliases=["un mask"],
    ),
    entry(
        id="peoplebyname",
        name="PeopleByName",
        tier=2,
        opt_out_url="https://www.peoplebyname.com/remove.php",
        allowed_hosts=["peoplebyname.com"],
        form_requires=["legal_name", "state", "optout_email"],
        match_with=["legal_name", "state"],
        form_optional=["phone"],
        aliases=["people by name"],
        notes="Guides say removal is per record. Repeat only for a second row that is also you.",
    ),
    entry(
        id="spyfly",
        name="SpyFly",
        tier=2,
        opt_out_url="https://www.spyfly.com/help-center/remove-my-public-record",
        allowed_hosts=["spyfly.com"],
        form_requires=["legal_name", "optout_email"],
        match_with=["legal_name"],
        form_optional=["phone"],
        aliases=["spy fly"],
    ),
    entry(
        id="familytreenow",
        name="FamilyTreeNow",
        tier=2,
        opt_out_url="https://www.familytreenow.com/optout",
        allowed_hosts=["familytreenow.com"],
        flow="optout_lookup",
        form_requires=["legal_name", "state", "optout_email"],
        match_with=["legal_name", "state"],
        form_optional=["phone"],
        aliases=["family tree now"],
        hint="Remove your own row. Do not open a relative's row and do not type a relative's name.",
    ),
    entry(
        id="socialcatfish",
        name="Social Catfish",
        tier=2,
        opt_out_url="https://socialcatfish.com/opt-out/",
        allowed_hosts=["socialcatfish.com"],
        form_requires=["legal_name", "optout_email"],
        match_with=["legal_name"],
        form_optional=["phone"],
        stop_if_asked=["a photo", "a face image"],
        aliases=["social catfish"],
        hint="If the page asks for a face photo, stop. A photo is a new biometric, and this packet does not include one.",
        typical_holdings=["name", "phone", "email", "address", "photo"],
    ),
    entry(
        id="infotracer",
        name="InfoTracer",
        tier=2,
        opt_out_url="https://infotracer.com/optout/",
        allowed_hosts=["infotracer.com"],
        form_requires=["legal_name", "optout_email"],
        match_with=["legal_name"],
        form_optional=["phone", "state", "city"],
        aliases=["info tracer"],
        hint="Use the web form. Do not fax or mail a copy of an ID.",
    ),
    entry(
        id="propertyrecs",
        name="PropertyRecs",
        tier=2,
        opt_out_url="https://dashboard.propertyrecs.com/opt-out",
        allowed_hosts=["dashboard.propertyrecs.com"],
        flow="optout_lookup",
        form_requires=["legal_name", "state", "optout_email"],
        match_with=["legal_name", "state"],
        form_optional=["city"],
        typical_holdings=["name", "address"],
        aliases=["property recs"],
        hint="Stay on dashboard.propertyrecs.com. Do not open a different property-search host.",
    ),
    entry(
        id="zoominfo",
        name="ZoomInfo",
        tier=3,
        kind="marketing",
        opt_out_url="https://privacyrequest.zoominfo.com/remove/verify",
        allowed_hosts=["privacyrequest.zoominfo.com"],
        form_requires=["legal_name", "optout_email"],
        match_with=["legal_name"],
        form_optional=[],
        typical_holdings=["name", "email", "employer"],
        aliases=["zoom info"],
        hint="Stay on privacyrequest.zoominfo.com. Do not open the ZoomInfo search product.",
        notes="This is a business-contact broker. The form does not get a personal phone unless you later add that field on purpose.",
        basis="Removal URL on the 2026-09-28 master list.",
    ),
    entry(
        id="acxiom",
        name="Acxiom",
        tier=3,
        kind="marketing",
        opt_out_url="https://www.acxiom.com/optout/",
        allowed_hosts=["acxiom.com"],
        form_requires=["legal_name", "city", "state", "postal_code", "optout_email"],
        match_with=["legal_name", "postal_code"],
        typical_holdings=["name", "address", "email"],
        processing="Marketing opt-outs often take longer than a people-search form.",
        notes="Acxiom sells consumer profiles to other businesses. There is no public people-search page to browse.",
        basis="Opt-out URL on the 2026-09-28 master list.",
    ),
    entry(
        id="epsilon",
        name="Epsilon",
        tier=3,
        kind="marketing",
        opt_out_url="https://legal.epsilon.com/dsr",
        allowed_hosts=["legal.epsilon.com"],
        form_requires=["legal_name", "optout_email"],
        match_with=["legal_name"],
        form_optional=["state", "postal_code"],
        typical_holdings=["name", "email", "address"],
        hint="Stay on legal.epsilon.com.",
        notes="Data-subject request page for marketing data. Not a public people search.",
        basis="Data-subject request URL on the 2026-09-28 master list.",
    ),
    entry(
        id="oracle",
        name="Oracle Data Cloud",
        tier=3,
        kind="marketing",
        opt_out_url="https://www.oracle.com/legal/privacy/privacy-choices/",
        allowed_hosts=["www.oracle.com"],
        form_requires=["optout_email"],
        match_with=["optout_email"],
        form_optional=["legal_name"],
        typical_holdings=["email"],
        aliases=["oracle"],
        hint="Stay on this privacy-choices URL. Do not create an Oracle account and do not open oracle.com search.",
        notes="This is an advertising-profile control, not a people-search listing.",
        basis="Privacy choices URL on the 2026-09-28 master list.",
    ),
    entry(
        id="donotcall",
        name="National Do Not Call Registry",
        tier=9,
        kind="registry",
        opt_out_url="https://www.donotcall.gov/register/reg.aspx",
        allowed_hosts=["donotcall.gov"],
        form_requires=["phone"],
        match_with=["phone"],
        form_optional=["legal_name", "optout_email"],
        verification="email or phone",
        processing="Lawful telemarketers have about 31 days to drop the number.",
        recheck_days=0,
        typical_holdings=["phone"],
        aliases=["do not call", "dnc", "do-not-call"],
        hint="Register this one phone. Do not add another number. This does not bind a caller who is already breaking the law.",
        notes="Official FTC registry for lawful telemarketing. Scam loan calls are a report to the FTC, not a Do Not Call problem.",
        basis="Official registry at donotcall.gov.",
    ),
    manual(
        id="spydialer",
        name="SpyDialer",
        tier=1,
        kind="people_search",
        opt_out_url="https://www.spydialer.com/",
        allowed_hosts=["spydialer.com"],
        form_requires=["phone"],
        match_with=["phone"],
        form_optional=["legal_name"],
        typical_holdings=["name", "phone", "address"],
        aliases=["spy dialer"],
        hint="",
        notes=(
            "2026 guides describe a footer control labeled Remove My Info and do not publish a stable "
            "deep link. The homepage is a search box, so Unlead does not give it to an agent. "
            "Open it yourself, use that footer control, and stop if you cannot find it."
        ),
        basis="Footer removal flow described by 2026 opt-out guides. No stable deep link verified for an agent.",
    ),
    manual(
        id="lexisnexis",
        name="LexisNexis",
        tier=9,
        kind="marketing",
        opt_out_url="https://consumer.risk.lexisnexis.com/opt",
        allowed_hosts=["consumer.risk.lexisnexis.com"],
        form_requires=[],
        match_with=[],
        typical_holdings=["name", "address"],
        recheck_days=365,
        aliases=["lexis nexis"],
        notes=(
            "The consumer opt-out uses an identity check that asks for more than a name and a phone. "
            "File it yourself if you need it. Do not paste an identity quiz into a chat agent."
        ),
        basis="Consumer opt-out URL on the 2026-09-28 master list.",
    ),
    manual(
        id="optoutprescreen",
        name="OptOutPrescreen",
        tier=9,
        kind="registry",
        opt_out_url="https://www.optoutprescreen.com/",
        allowed_hosts=["optoutprescreen.com"],
        form_requires=[],
        match_with=[],
        typical_holdings=["name", "address"],
        recheck_days=1825,
        verification="identity",
        processing="Five years for the online opt-out. The mailed form is the permanent one.",
        aliases=["opt out prescreen", "prescreen", "optout prescreen"],
        notes=(
            "Official opt-out for prescreened firm offers of credit and insurance, run for the credit bureaus. "
            "The form asks for your Social Security number and date of birth. "
            "Unlead does not store those and does not put them in an agent packet. "
            "Five years can be done on the site. Permanent is a form you mail back. "
            "Phone 1-888-567-8688 is the same program."
        ),
        basis="Official industry opt-out required by the Fair Credit Reporting Act for prescreened offers.",
    ),
    manual(
        id="drop",
        name="California DROP",
        tier=9,
        kind="registry",
        opt_out_url="https://consumer.drop.privacy.ca.gov/",
        allowed_hosts=["consumer.drop.privacy.ca.gov"],
        form_requires=[],
        match_with=[],
        typical_holdings=["name", "address"],
        recheck_days=0,
        aliases=["california drop", "delete act"],
        notes=(
            "California Delete Request and Opt-out Platform, for California residents. "
            "It verifies residency and then sends a deletion request to registered data brokers. "
            "Residents of other states use the per-site requests. Do not send an agent through the residency check."
        ),
        basis="California Privacy Protection Agency DROP site.",
    ),
    manual(
        id="equifax",
        name="Equifax marketing opt-out",
        tier=9,
        kind="registry",
        opt_out_url="https://myprivacy.equifax.com/opt-in-opt-out/personal-info/",
        allowed_hosts=["myprivacy.equifax.com"],
        form_requires=[],
        match_with=[],
        typical_holdings=["name", "address"],
        recheck_days=0,
        aliases=["equifax"],
        notes=(
            "Marketing choices at Equifax. The sign-in or identity check can ask for more than this case stores. "
            "Do it yourself. A credit freeze is a separate page and a separate decision."
        ),
        basis="Marketing privacy URL on the 2026-09-28 master list.",
    ),
    manual(
        id="experian",
        name="Experian marketing opt-out",
        tier=9,
        kind="registry",
        opt_out_url="https://consumerprivacy.experian.com/",
        allowed_hosts=["consumerprivacy.experian.com"],
        form_requires=[],
        match_with=[],
        typical_holdings=["name", "address"],
        recheck_days=0,
        aliases=["experian"],
        notes=(
            "Marketing and privacy requests at Experian. Identity checks stay in your browser. "
            "This is separate from OptOutPrescreen and separate from a credit freeze."
        ),
        basis="Consumer privacy URL on the 2026-09-28 master list.",
    ),
    manual(
        id="transunion",
        name="TransUnion privacy",
        tier=9,
        kind="registry",
        opt_out_url="https://www.transunion.com/privacy",
        allowed_hosts=["www.transunion.com"],
        form_requires=[],
        match_with=[],
        typical_holdings=["name", "address"],
        recheck_days=0,
        aliases=["transunion", "trans union"],
        notes="Start at the privacy page and do the identity check yourself. Do not hand a chat agent your TransUnion login.",
        basis="Privacy URL on the 2026-09-28 master list.",
    ),
    manual(
        id="pimeyes",
        name="PimEyes",
        tier=9,
        kind="biometric",
        opt_out_url="https://pimeyes.com/en/opt-out",
        allowed_hosts=["pimeyes.com"],
        form_requires=[],
        match_with=[],
        typical_holdings=["photo"],
        stop_if_asked=["a photo", "a face image", "an ID image"],
        notes=(
            "Removal asks for a face photo or an ID image. That gives the site a new biometric. "
            "Unlead does not draft an upload. Skip this unless you already know they have a photo, "
            "and then use their page yourself."
        ),
        basis="Opt-out URL on the 2026-09-28 master list.",
    ),
    manual(
        id="facecheck",
        name="FaceCheck.ID",
        tier=9,
        kind="biometric",
        opt_out_url="https://facecheck.id/en/RemoveMyPhotos",
        allowed_hosts=["facecheck.id"],
        form_requires=[],
        match_with=[],
        typical_holdings=["photo"],
        aliases=["facecheck", "face check"],
        notes=(
            "Removal asks for a photo or an ID. Unlead does not draft an upload and does not write an agent packet."
        ),
        basis="Removal URL on the 2026-09-28 master list.",
    ),
    manual(
        id="google-results",
        name="Google results about you",
        tier=9,
        kind="search_engine",
        opt_out_url="https://support.google.com/websearch/answer/9673730",
        allowed_hosts=["support.google.com"],
        form_requires=[],
        match_with=[],
        typical_holdings=["name", "phone", "address"],
        recheck_days=90,
        aliases=["google", "results about you"],
        notes=(
            "After a broker page comes down, a search snippet can remain. "
            "Google's tool uses your Google account. Do that sign-in yourself. "
            "This removes results. It does not delete the broker's copy."
        ),
        basis="Google help page for Results about you.",
    ),
    manual(
        id="ftc-report",
        name="FTC fraud report",
        tier=9,
        kind="registry",
        opt_out_url="https://reportfraud.ftc.gov/",
        allowed_hosts=["reportfraud.ftc.gov"],
        form_requires=[],
        match_with=[],
        typical_holdings=["phone"],
        recheck_days=0,
        aliases=["ftc", "report fraud"],
        notes=(
            "Report a scam loan call here. This is not a broker opt-out. "
            "Write down the number, the time, and the pitch before you start. "
            "Do not give the caller a code, a payment, or a new account number. "
            "Unlead does not file this report for you."
        ),
        basis="Federal Trade Commission report-fraud site.",
    ),
    closed(
        "radaris",
        "Radaris",
        "As of the 2026-09-28 check, the domain was reported transferred after a New Jersey Daniel's Law case. "
        + _CLOSED,
    ),
    closed(
        "peekyou",
        "PeekYou",
        "As of the 2026-09-28 check, the domain was reported under new control after a Daniel's Law case. "
        + _CLOSED,
    ),
    closed(
        "rehold",
        "Rehold",
        "As of the 2026-09-28 check, the domain showed a transferred-by-court-order notice. " + _CLOSED,
    ),
    closed(
        "nuwber",
        "Nuwber",
        "As of the 2026-09-28 check, the domain did not resolve to a people-search site. " + _CLOSED,
    ),
    closed(
        "homemetry",
        "Homemetry",
        "As of the 2026-09-28 check, the domain was parked. " + _CLOSED,
    ),
    closed(
        "neighborreport",
        "NeighborReport",
        "As of the 2026-09-28 check, the domain did not resolve. " + _CLOSED,
    ),
    closed(
        "publicdatausa",
        "PublicDataUSA",
        "As of the 2026-09-28 check, the domain did not resolve. " + _CLOSED,
    ),
    closed(
        "usa-official",
        "USA-Official",
        "As of the 2026-09-28 check, this site was off the live people-search list. " + _CLOSED,
    ),
]
