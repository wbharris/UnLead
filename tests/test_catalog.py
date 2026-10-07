from unlead.brokers import CATALOG_COUNT, CATALOG_REVISED
from unlead.catalog import load_catalog
from unlead.policy import ALLOWED_FIELDS


PINNED = {
    "spokeo": "https://www.spokeo.com/optout",
    "beenverified": "https://www.beenverified.com/app/optout/search",
    "whitepages": "https://www.whitepages.com/suppression-requests",
    "peopleconnect": "https://suppression.peopleconnect.us/login",
    "mylife": "https://www.mylife.com/privacyrequest",
    "fastpeoplesearch": "https://www.fastpeoplesearch.com/optout",
    "truepeoplesearch": "https://www.truepeoplesearch.com/removal",
    "donotcall": "https://www.donotcall.gov/register/reg.aspx",
    "optoutprescreen": "https://www.optoutprescreen.com/",
}


def test_catalog_pins_and_shape():
    rows = load_catalog()
    assert len(rows) == CATALOG_COUNT == 52
    assert CATALOG_REVISED == "2026-10-07"
    by_id = {row["id"]: row for row in rows}
    for broker_id, url in PINNED.items():
        assert by_id[broker_id]["opt_out_url"] == url
    assert by_id["radaris"]["status"] == "closed"
    assert by_id["radaris"]["opt_out_url"] is None
    assert by_id["optoutprescreen"]["status"] == "human_only"
    assert by_id["optoutprescreen"]["agent_allowed"] is False
    assert by_id["pimeyes"]["kind"] == "biometric"
    for row in rows:
        assert "ssn" in row["never_send"]
        for field in row["form_requires"] + row["match_with"] + row["form_optional"]:
            assert field in ALLOWED_FIELDS
        if row["status"] == "open":
            assert row["agent_allowed"] is True
            assert row["opt_out_url"].startswith("https://")
        assert "http://" not in (row.get("hint") or "")
        assert "https://" not in (row.get("hint") or "")
