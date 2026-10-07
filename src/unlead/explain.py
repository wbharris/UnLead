"""Short explanations. No links in this module. URLs live on catalog entries."""

WORKING_PROMPT = """Score each broker in the UnLead catalog against the name and phone stored in this local case.
Say which of those fields each opt-out form actually needs, and which fields the case will withhold.
For the sites I select, record only the categories I confirm I saw on my own listing.
Write the exact opt-out for each selected site, then write one agent packet per site that is ready.
I will paste a single packet into a browser agent I already use. That agent opens one official opt-out URL and enters only the packet's fields."""

START = """
UnLead keeps a case file on this computer and writes opt-out requests for your own listings.

1. `unlead init --case DIR --name "Your Name" --phone "your number"`
2. `unlead probe --case DIR` to see what name and phone are enough for, and what each form still wants.
3. `unlead select --tier 1 --case DIR` for the high-traffic people-search sites.
4. `unlead ask --case DIR` and answer only the fields those sites still require. Press Enter to skip a field.
5. `unlead holdings set SITE --seen yes --has phone,address --case DIR` after you have looked at your own row.
6. `unlead letters --case DIR` writes one request per selected site.
7. `unlead handoff --case DIR` writes one agent file per site that is ready.
8. Paste one agent file into the browser agent you use. Finish that site. Then paste the next file.
9. `unlead mark SITE submitted --case DIR` and check again when status shows a recheck date. Listings come back.

`unlead prompt` prints the working prompt. `unlead explain loan` is the loan-call context.
""".strip()

FIELDS = """
The experiment is name and phone, scored locally against the catalog.

Name and phone are enough for you to tell your own row from someone else with the same name. The phone is the part that separates the rows. A name alone collides with other people.

The opt-out form often wants a different set. Spokeo's form wants the listing URL and an email, so the letter withholds the phone even though the phone is what you used to recognize the row. A reverse-phone site wants the phone and withholds the name when the form does not ask for it.

An opt-out email is the field most forms add. Use an inbox that is not your main one if you have it. The letter tells the broker not to enroll that address. Some of them will ignore that. A separate inbox limits the damage.

UnLead will not store a Social Security number, a date of birth, a government ID, a password, or a biometric. Sites that ask for those are manual guides. You file them in your own browser if you decide to.
""".strip()

AGENT = """
The handoff file is for a browser agent you already run. UnLead does not connect to that agent and does not send the file.

Each file is one site. The agent may open the opt-out URL in the DATA block and fill the fields in that block. DATA is data. A line inside your name or your listing URL does not become an instruction.

The agent is told to stop for a CAPTCHA, a phone call, an SMS code, a payment, a password, or any ask for a Social Security number, an ID, a date of birth, or a face photo. You finish those steps. You also open the confirmation email yourself.

Do not paste two site files into one session. Do not paste a manual guide. Those guides are for pages that ask for more than the case is allowed to hold.
""".strip()

LOAN = """
A loan application can put your phone in front of strangers in three different ways.

People-search sites already publish name, phone, address, and relatives. A caller who bought a lead can match you there. UnLead writes the opt-out for those sites from the fields each form requires.

Prescreened firm offers are the credit-bureau product. After a credit pull, bureaus have been allowed to sell you as someone shopping for credit. For a residential mortgage, the Homebuyers Privacy Protection Act, Public Law 119-36, signed September 5, 2025, limits that sale starting in March 2026. A bureau may still furnish the lead to a lender you authorized, to the company that originated or services your current mortgage, or to a bank or credit union where you already have an account. Other kinds of loans can still become prescreened firm offers. The official opt-out is OptOutPrescreen: five years on the site, or permanent by a form you mail back. That form asks for a Social Security number and a date of birth. Run `unlead guide optoutprescreen` and file it yourself. UnLead does not put those into an agent packet. A GAO review dated October 6, 2026 says it is too early to know how much the mortgage rule cuts the calls.

Scam calls are the third pile. The caller is not a lender, the Do Not Call Registry does not bind them, and the pitch often asks for a code or a fee. Save the number, the time, and the words they used. Do not give them a code, a payment, or a new account number. Run `unlead guide ftc-report` and file that report yourself.

`unlead guide donotcall` is still worth doing for lawful telemarketing. It is a different list from the scam calls and from OptOutPrescreen.
""".strip()

TOPICS = {
    "start": START,
    "fields": FIELDS,
    "agent": AGENT,
    "loan": LOAN,
}
