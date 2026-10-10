import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_health_endpoint(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    data = r.get_json()
    assert data["status"] == "ok"
    assert data["detector_mode"] in ("trained", "keyword_fallback")


def test_frontend_and_assets_are_served(client):
    page = client.get("/")
    assert page.status_code == 200
    assert b"SmartIntent" in page.data
    assert b"/static/style.css" in page.data
    assert b"/static/script.js" in page.data

    assert client.get("/static/style.css").status_code == 200
    assert client.get("/static/script.js").status_code == 200


def test_intents_endpoint(client):
    r = client.get("/api/intents")
    assert r.status_code == 200
    data = r.get_json()
    assert "intents" in data
    assert any(i["label"] == "order_tracking" for i in data["intents"])


def test_analyze_empty_message(client):
    r = client.post("/api/analyze", json={"message": "   "})
    assert r.status_code == 400
    data = r.get_json()
    assert data["error"]["code"] == "empty_message"


def test_analyze_non_string_message(client):
    r = client.post("/api/analyze", json={"message": 12345})
    assert r.status_code == 400
    assert r.get_json()["error"]["code"] == "invalid_message"


def test_analyze_symbol_only_message(client):
    r = client.post("/api/analyze", json={"message": "12345 !!! @@"})
    assert r.status_code == 422
    assert r.get_json()["error"]["code"] == "no_text_content"


def test_analyze_valid_message_contract(client):
    r = client.post(
        "/api/analyze",
        json={"message": "Where is my order #48213? It was supposed to arrive yesterday."},
    )
    assert r.status_code == 200
    data = r.get_json()
    assert "intents" in data
    assert "entities" in data
    assert "status" in data
    assert "urgency" in data
    assert "route_to" in data
    assert "model" in data
    assert data["intents"][0]["label"] == "order_tracking"
    assert any(e["type"] == "order_id" and e["value"] == "48213" for e in data["entities"])


def test_analyze_batch(client):
    r = client.post(
        "/api/analyze",
        json={"messages": ["Where is my order #48213?", "Cancel ORD-77120"]},
    )
    # Testing batch endpoint
    r_batch = client.post(
        "/api/analyze/batch",
        json={"messages": ["Where is my order #48213?", "", "Cancel ORD-77120"]},
    )
    assert r_batch.status_code == 200
    results = r_batch.get_json()["results"]
    assert len(results) == 3
    assert results[0]["result"]["intents"][0]["label"] == "order_tracking"
    assert results[1]["error"]["code"] == "empty_message"
    assert results[2]["result"]["intents"][0]["label"] == "order_cancellation"


def test_feedback_confirm_and_correct(client):
    # 1. First analyze a message to create an entry
    res = client.post("/api/analyze", json={"message": "My shoes are torn and damaged"}).get_json()
    pid = res.get("id")
    if pid is not None:
        # Confirm
        r_conf = client.post("/api/feedback", json={"prediction_id": pid, "action": "confirm"})
        assert r_conf.status_code == 200
        assert r_conf.get_json()["review_status"] == "confirmed"

        # Correct
        r_corr = client.post(
            "/api/feedback",
            json={"prediction_id": pid, "action": "correct", "corrected_intent": "refund_request"},
        )
        assert r_corr.status_code == 200
        assert r_corr.get_json()["review_status"] == "corrected"
        assert r_corr.get_json()["corrected_intent"] == "refund_request"


def test_stats_and_history(client):
    r_stats = client.get("/api/stats")
    assert r_stats.status_code == 200
    stats_data = r_stats.get_json()
    assert "total" in stats_data
    assert "by_intent" in stats_data

    r_hist = client.get("/api/history?limit=10")
    assert r_hist.status_code == 200
    assert "items" in r_hist.get_json()
