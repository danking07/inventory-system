from unittest.mock import Mock, patch

import requests

import cli

ITEM = {"id": 1, "product_name": "Milk", "brands": "Silk", "price": 4.0,
        "stock": 5, "barcode": "123", "ingredients_text": "water"}


def fake_response(data, ok=True, status=200):
    """A pretend answer from our Flask API."""
    response = Mock()
    response.ok = ok
    response.status_code = status
    response.json.return_value = data
    return response


def typed(*answers):
    """Pretend the user types these answers, one per input() call."""
    answers = iter(answers)
    return lambda _prompt="": next(answers)


# ---------- send_request ----------
def test_send_request_success():
    with patch("cli.requests.request", return_value=fake_response({"a": 1})):
        assert cli.send_request("GET", "/inventory") == {"a": 1}


def test_send_request_server_down(capsys):
    with patch("cli.requests.request", side_effect=requests.exceptions.ConnectionError):
        assert cli.send_request("GET", "/inventory") is None
    assert "Could not connect" in capsys.readouterr().out


def test_send_request_api_error(capsys):
    response = fake_response({"error": "item not found"}, ok=False, status=404)
    with patch("cli.requests.request", return_value=response):
        assert cli.send_request("GET", "/inventory/9") is None
    assert "item not found" in capsys.readouterr().out


# ---------- input helpers ----------
def test_get_whole_number_asks_again(capsys):
    with patch("builtins.input", typed("abc", "-3", "7")):
        assert cli.get_whole_number("n: ") == 7
    assert "whole number" in capsys.readouterr().out


def test_get_price_asks_again(capsys):
    with patch("builtins.input", typed("abc", "-1", "2.5")):
        assert cli.get_price("p: ") == 2.5
    assert "price" in capsys.readouterr().out


# ---------- menu options ----------
def test_show_all_items(capsys):
    with patch("cli.requests.request", return_value=fake_response([ITEM])):
        cli.show_all_items()
    assert "Milk" in capsys.readouterr().out


def test_show_all_items_empty(capsys):
    with patch("cli.requests.request", return_value=fake_response([])):
        cli.show_all_items()
    assert "empty" in capsys.readouterr().out


def test_show_one_item(capsys):
    with patch("builtins.input", typed("1")), \
         patch("cli.requests.request", return_value=fake_response(ITEM)):
        cli.show_one_item()
    assert "water" in capsys.readouterr().out


def test_add_item_sends_the_right_data():
    with patch("builtins.input", typed("Milk", "Silk", "123", "4.5", "10")), \
         patch("cli.requests.request", return_value=fake_response(ITEM, status=201)) as fake:
        cli.add_item()
    assert fake.call_args.args[0] == "POST"
    sent = fake.call_args.kwargs["json"]
    assert sent["product_name"] == "Milk" and sent["price"] == 4.5 and sent["stock"] == 10


def test_add_item_empty_name_sends_nothing(capsys):
    with patch("builtins.input", typed("")), patch("cli.requests.request") as fake:
        cli.add_item()
    fake.assert_not_called()
    assert "can't be empty" in capsys.readouterr().out


def test_update_item_sends_only_the_price():
    with patch("builtins.input", typed("1", "9.99", "")), \
         patch("cli.requests.request", return_value=fake_response(ITEM)) as fake:
        cli.update_item()
    assert fake.call_args.args[0] == "PATCH"
    assert fake.call_args.kwargs["json"] == {"price": 9.99}


def test_update_item_nothing_to_change(capsys):
    with patch("builtins.input", typed("1", "", "")), patch("cli.requests.request") as fake:
        cli.update_item()
    fake.assert_not_called()
    assert "Nothing to change" in capsys.readouterr().out


def test_update_item_bad_price(capsys):
    with patch("builtins.input", typed("1", "abc")), patch("cli.requests.request") as fake:
        cli.update_item()
    fake.assert_not_called()
    assert "not a valid price" in capsys.readouterr().out


def test_delete_item(capsys):
    with patch("builtins.input", typed("1")), \
         patch("cli.requests.request", return_value=fake_response({"message": "item deleted"})) as fake:
        cli.delete_item()
    assert fake.call_args.args[0] == "DELETE"
    assert "Item deleted" in capsys.readouterr().out


def test_find_and_add_from_openfoodfacts():
    product = {"product_name": "Nutella", "brands": "Ferrero", "barcode": "9"}
    responses = [fake_response(product), fake_response(ITEM, status=201)]
    with patch("builtins.input", typed("b", "9", "y", "6.5", "12")), \
         patch("cli.requests.request", side_effect=responses) as fake:
        cli.find_on_openfoodfacts()
    assert fake.call_count == 2
    assert fake.call_args.args[1].endswith("/inventory/import")
    assert fake.call_args.kwargs["json"]["price"] == 6.5


def test_find_but_do_not_add():
    product = {"product_name": "Nutella", "brands": "Ferrero", "barcode": "9"}
    with patch("builtins.input", typed("n", "nutella", "n")), \
         patch("cli.requests.request", return_value=fake_response(product)) as fake:
        cli.find_on_openfoodfacts()
    assert fake.call_count == 1


def test_find_bad_choice():
    with patch("builtins.input", typed("x")), patch("cli.requests.request") as fake:
        cli.find_on_openfoodfacts()
    fake.assert_not_called()


# ---------- main menu ----------
def test_main_quits(capsys):
    with patch("builtins.input", typed("q")):
        cli.main()
    assert "Goodbye" in capsys.readouterr().out


def test_main_invalid_choice_then_quit(capsys):
    with patch("builtins.input", typed("x", "q")):
        cli.main()
    assert "not an option" in capsys.readouterr().out