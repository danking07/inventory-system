from unittest.mock import patch

from off_client import OpenFoodFactsError

NUTELLA = {"product_name": "Nutella", "brands": "Ferrero",
           "ingredients_text": "Sugar, palm oil, hazelnuts", "barcode": "123"}


# ---------- CRUD ----------
def test_get_all(client):
    response = client.get("/inventory")
    assert response.status_code == 200
    assert len(response.get_json()) == 2


def test_get_one(client):
    response = client.get("/inventory/1")
    assert response.status_code == 200
    assert response.get_json()["product_name"] == "Organic Almond Milk"


def test_get_one_missing(client):
    assert client.get("/inventory/999").status_code == 404


def test_create(client):
    response = client.post("/inventory", json={"product_name": "Oats", "price": 2.5, "stock": 10})
    assert response.status_code == 201
    assert response.get_json()["id"] == 3
    assert len(client.get("/inventory").get_json()) == 3


def test_create_requires_name(client):
    assert client.post("/inventory", json={"price": 1}).status_code == 400


def test_create_rejects_bad_price(client):
    response = client.post("/inventory", json={"product_name": "X", "price": -5})
    assert response.status_code == 400


def test_create_rejects_no_body(client):
    assert client.post("/inventory").status_code == 400


def test_patch(client):
    response = client.patch("/inventory/1", json={"price": 5.99, "stock": 7})
    assert response.status_code == 200
    assert response.get_json()["price"] == 5.99
    assert client.get("/inventory/1").get_json()["stock"] == 7


def test_patch_missing(client):
    assert client.patch("/inventory/999", json={"price": 1}).status_code == 404


def test_patch_cannot_change_id(client):
    assert client.patch("/inventory/1", json={"id": 50}).status_code == 400


def test_patch_bad_stock(client):
    assert client.patch("/inventory/1", json={"stock": "lots"}).status_code == 400


def test_delete(client):
    assert client.delete("/inventory/1").status_code == 200
    assert client.get("/inventory/1").status_code == 404


def test_delete_missing(client):
    assert client.delete("/inventory/999").status_code == 404


def test_ids_not_reused_after_delete(client):
    client.delete("/inventory/1")
    response = client.post("/inventory", json={"product_name": "New"})
    assert response.get_json()["id"] == 3


# ---------- OpenFoodFacts routes (the real API is faked) ----------
def test_lookup_by_barcode(client):
    with patch("app.fetch_by_barcode", return_value=NUTELLA) as fake:
        response = client.get("/lookup?barcode=123")
    assert response.status_code == 200
    assert response.get_json()["product_name"] == "Nutella"
    fake.assert_called_once_with("123")


def test_lookup_by_name(client):
    with patch("app.search_by_name", return_value=NUTELLA):
        assert client.get("/lookup?name=nutella").status_code == 200


def test_lookup_needs_a_parameter(client):
    assert client.get("/lookup").status_code == 400


def test_lookup_not_found(client):
    with patch("app.fetch_by_barcode", return_value=None):
        assert client.get("/lookup?barcode=000").status_code == 404


def test_lookup_when_api_is_down(client):
    with patch("app.fetch_by_barcode", side_effect=OpenFoodFactsError("down")):
        assert client.get("/lookup?barcode=123").status_code == 502


def test_import_adds_to_inventory(client):
    with patch("app.fetch_by_barcode", return_value=NUTELLA):
        response = client.post("/inventory/import",
                               json={"barcode": "123", "price": 6.5, "stock": 12})
    assert response.status_code == 201
    item = response.get_json()
    assert item["id"] == 3 and item["price"] == 6.5 and item["brands"] == "Ferrero"
    assert len(client.get("/inventory").get_json()) == 3


def test_import_not_found_adds_nothing(client):
    with patch("app.fetch_by_barcode", return_value=None):
        assert client.post("/inventory/import", json={"barcode": "0"}).status_code == 404
    assert len(client.get("/inventory").get_json()) == 2


def test_import_bad_price(client):
    with patch("app.fetch_by_barcode", return_value=NUTELLA):
        response = client.post("/inventory/import", json={"barcode": "1", "price": -1})
    assert response.status_code == 400