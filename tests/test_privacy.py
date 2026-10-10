from ml_model.privacy import mask_pii


def test_masks_card_phone_email():
    text = "card 4111 1111 1111 1111 call 9876543210 mail asha@example.com"
    out, counts = mask_pii(text)
    assert "4111" not in out
    assert "9876543210" not in out
    assert "asha@example.com" not in out
    assert "[CARD]" in out
    assert "[PHONE]" in out
    assert "[EMAIL]" in out
    assert counts.get("CARD") == 1
    assert counts.get("PHONE") == 1
    assert counts.get("EMAIL") == 1


def test_protected_order_id_not_masked():
    text = "order 9876543210 please check"
    start = text.index("9876543210")
    # Mark order ID span as protected
    out, counts = mask_pii(text, protected_spans=[(start, start + 10)])
    assert "9876543210" in out
    assert counts == {}
