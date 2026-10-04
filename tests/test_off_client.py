from unittest.mock import Mock, patch

import pytest
import requests

import off_client


def fake_response(data):
    """A pretend answer from OpenFoodFacts."""
    response = Mock()
    response.json.return_value = data
    response.raise_for_status.return_value = None
    return response


def test_fetch_by_barcode_success():
    data = {"status": 1, "product": {"product_name": "Organic Almond Milk",
            "brands": "Silk", "ingredients_text": "Filtered water, almonds"}}
    with patch("off_client.requests.get", return_value=fake_response(data)):
        product = off_client.fetch_by_barcode("111")
    assert product["product_name"] == "Organic Almond Milk"
    assert product["barcode"] == "111"


def test_fetch_by_barcode_not_found():
    with patch("off_client.requests.get", return_value=fake_response({"status": 0})):
        assert off_client.fetch_by_barcode("000") is None


def test_missing_name_becomes_unknown():
    data = {"status": 1, "product": {"brands": "Silk"}}
    with patch("off_client.requests.get", return_value=fake_response(data)):
        assert off_client.fetch_by_barcode("111")["product_name"] == "Unknown"


def test_search_by_name_success():
    data = {"products": [{"product_name": "Nutella", "brands": "Ferrero", "code": "999"}]}
    with patch("off_client.requests.get", return_value=fake_response(data)):
        product = off_client.search_by_name("nutella")
    assert product["barcode"] == "999"


def test_search_by_name_no_results():
    with patch("off_client.requests.get", return_value=fake_response({"products": []})):
        assert off_client.search_by_name("zzzz") is None


def test_network_error_raises_our_error():
    with patch("off_client.requests.get", side_effect=requests.exceptions.ConnectionError):
        with pytest.raises(off_client.OpenFoodFactsError):
            off_client.fetch_by_barcode("111")


def test_bad_json_raises_our_error():
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.side_effect = ValueError
    with patch("off_client.requests.get", return_value=response):
        with pytest.raises(off_client.OpenFoodFactsError):
            off_client.search_by_name("x")