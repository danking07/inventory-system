# cli.py
# A simple menu for managing the inventory.
# Start the server first (python app.py), then run: python cli.py

import requests

BASE_URL = "http://127.0.0.1:5000"


def send_request(method, path, data=None, params=None):
    """Send a request to the Flask API and return the answer.
    If something goes wrong, print a message and return None."""
    url = BASE_URL + path
    try:
        response = requests.request(method, url, json=data, params=params, timeout=10)
    except requests.exceptions.RequestException:
        print("Could not connect to the API. Is the server running?")
        return None

    try:
        result = response.json()
    except ValueError:
        result = {}

    if not response.ok:
        print("Something went wrong:", result.get("error", response.status_code))
        return None

    return result


def get_whole_number(message):
    """Ask until the user types a whole number (0 or more)."""
    while True:
        text = input(message).strip()
        if text.isdigit():
            return int(text)
        print("Please type a whole number, like 5.")


def get_price(message):
    """Ask until the user types a price (0 or more)."""
    while True:
        text = input(message).strip()
        try:
            price = float(text)
            if price >= 0:
                return price
        except ValueError:
            pass
        print("Please type a price, like 4.99.")


def print_item(item):
    print(f"  ID {item['id']}: {item['product_name']} ({item['brands']})")
    print(f"     Price: ${item['price']}   Stock: {item['stock']}   Barcode: {item['barcode']}")


def show_all_items():
    items = send_request("GET", "/inventory")
    if items is None:
        return
    if len(items) == 0:
        print("The inventory is empty.")
        return
    for item in items:
        print_item(item)


def show_one_item():
    item_id = get_whole_number("Item ID: ")
    item = send_request("GET", f"/inventory/{item_id}")
    if item:
        print_item(item)
        print("     Ingredients:", item["ingredients_text"] or "not listed")


def add_item():
    name = input("Product name: ").strip()
    if name == "":
        print("The name can't be empty.")
        return

    new_item = {
        "product_name": name,
        "brands": input("Brand: ").strip(),
        "barcode": input("Barcode: ").strip(),
        "price": get_price("Price: "),
        "stock": get_whole_number("Stock: "),
    }
    item = send_request("POST", "/inventory", data=new_item)
    if item:
        print("Item added!")
        print_item(item)


def update_item():
    item_id = get_whole_number("ID of the item to update: ")
    changes = {}

    answer = input("New price (press Enter to keep the old one): ").strip()
    if answer != "":
        try:
            changes["price"] = float(answer)
        except ValueError:
            print("That's not a valid price.")
            return

    answer = input("New stock (press Enter to keep the old one): ").strip()
    if answer != "":
        if not answer.isdigit():
            print("Stock must be a whole number.")
            return
        changes["stock"] = int(answer)

    if len(changes) == 0:
        print("Nothing to change.")
        return

    item = send_request("PATCH", f"/inventory/{item_id}", data=changes)
    if item:
        print("Item updated!")
        print_item(item)


def delete_item():
    item_id = get_whole_number("ID of the item to delete: ")
    result = send_request("DELETE", f"/inventory/{item_id}")
    if result:
        print("Item deleted.")


def find_on_openfoodfacts():
    choice = input("Search by barcode (b) or name (n)? ").strip().lower()
    if choice == "b":
        search = {"barcode": input("Barcode: ").strip()}
    elif choice == "n":
        search = {"name": input("Product name: ").strip()}
    else:
        print("Please type b or n.")
        return

    product = send_request("GET", "/lookup", params=search)
    if not product:
        return

    print(f"Found: {product['product_name']} ({product['brands']})")
    want_to_add = input("Add it to the inventory? (y/n): ").strip().lower()
    if want_to_add != "y":
        return

    search["price"] = get_price("Price: ")
    search["stock"] = get_whole_number("Stock: ")
    item = send_request("POST", "/inventory/import", data=search)
    if item:
        print("Item added!")
        print_item(item)


def main():
    while True:
        print()
        print("===== Inventory Manager =====")
        print("1. Show all items")
        print("2. Show one item")
        print("3. Add an item")
        print("4. Update price or stock")
        print("5. Delete an item")
        print("6. Find a product on OpenFoodFacts")
        print("q. Quit")
        choice = input("Choose an option: ").strip().lower()

        if choice == "1":
            show_all_items()
        elif choice == "2":
            show_one_item()
        elif choice == "3":
            add_item()
        elif choice == "4":
            update_item()
        elif choice == "5":
            delete_item()
        elif choice == "6":
            find_on_openfoodfacts()
        elif choice == "q":
            print("Goodbye!")
            break
        else:
            print("That's not an option, try again.")


if __name__ == "__main__":
    main()