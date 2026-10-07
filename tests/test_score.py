from unlead.catalog import by_id
from unlead.score import NAME_AND_PHONE, NAME_ONLY, field_plan, questions_for, recognition


def test_name_and_phone_split_from_what_a_form_sends():
    level, text = recognition({"legal_name", "phone"})
    assert level == "name_phone"
    assert text == NAME_AND_PHONE
    assert recognition({"legal_name"})[1] == NAME_ONLY

    supplied = {"legal_name", "phone"}
    spokeo = field_plan(by_id("spokeo"), supplied)
    assert spokeo["letter_ready"] is False
    assert spokeo["missing"] == ["profile_url", "optout_email"]
    assert spokeo["withheld"] == ["legal_name", "phone"]
    assert spokeo["send"] == []

    phonebook = field_plan(by_id("usphonebook"), supplied)
    assert "phone" in phonebook["send"]
    assert "legal_name" in phonebook["withheld"]
    assert "optout_email" in phonebook["missing"]

    prescreen = field_plan(by_id("optoutprescreen"), supplied)
    assert prescreen["agent_ready"] is False
    assert prescreen["letter_ready"] is False


def test_optional_fields_stay_out_until_asked():
    broker = by_id("spokeo")
    supplied = {"legal_name", "phone", "optout_email", "city", "profile_url"}
    quiet = field_plan(broker, supplied)
    assert quiet["letter_ready"] is True
    assert quiet["send"] == ["optout_email", "profile_url"]
    assert "phone" in quiet["withheld"]
    assert "city" in quiet["withheld"]
    loud = field_plan(broker, supplied, include_optional=True)
    assert "phone" in loud["send"]
    assert "city" in loud["send"]


def test_questions_ask_only_for_missing_required_fields():
    case = {
        "identifiers": {"legal_name": "Ada Lovelace", "phone": "555-0148"},
        "sites": {
            "spokeo": {"selected": True, "profile_url": ""},
            "beenverified": {"selected": True},
            "acxiom": {"selected": False},
            "optoutprescreen": {"selected": True},
        },
    }
    questions = questions_for(case)
    fields = [question.field for question in questions]
    assert "city" not in fields
    assert "phone" not in fields
    assert "ssn" not in fields
    assert "optout_email" in fields
    assert "state" in fields
    assert "profile_url" in fields
    email = next(question for question in questions if question.field == "optout_email")
    assert "Spokeo" in email.brokers
    assert "BeenVerified" in email.brokers
    assert "Acxiom" not in email.brokers
    url = next(question for question in questions if question.field == "profile_url")
    assert url.broker_id == "spokeo"
    assert "Social Security" not in url.prompt
