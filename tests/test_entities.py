from ml_model import config
from ml_model.entity_extractor import EntityExtractor

extractor = EntityExtractor(config.PRODUCTS_PATH)


def found(text: str):
    return {(e["type"], e["value"]) for e in extractor.extract(text)}


def test_order_id_hash():
    f = found("Where is my order #48213?")
    assert ("order_id", "48213") in f


def test_order_id_prefixed():
    f = found("Cancel ORD-77120 please")
    assert ("order_id", "ORD-77120") in f


def test_amount_extraction():
    f = found("Rs. 2,499 was deducted from my account")
    assert ("amount", "INR 2499") in f


def test_relative_date():
    f = found("It arrived yesterday and was defective")
    assert ("date", "yesterday") in f
    assert ("issue", "defective") in f


def test_random_digits_not_treated_as_order():
    res = [e for e in extractor.extract("I waited 45678 minutes") if e["type"] == "order_id"]
    assert len(res) == 0


def test_product_gazetteer():
    f = found("Does the Galaxy M14 have 5G support?")
    assert ("product", "Galaxy M14") in f
