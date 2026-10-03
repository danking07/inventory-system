from flask import Flask, jsonify, request

from off_client import OpenFoodFactsError, fetch_by_barcode, search_by_name

app = Flask(__name__)

# Mock database: a list of dictionaries
inventory = [
    {"id": 1, "product_name": "Organic Almond Milk", "brands": "Silk",
     "ingredients_text": "Filtered water, almonds, cane sugar",
     "barcode": "0025293001213", "price": 4.99, "stock": 20},
    {"id": 2, "product_name": "Crunchy Peanut Butter", "brands": "Jif",
     "ingredients_text": "Roasted peanuts, sugar, palm oil, salt",
     "barcode": "0051500240144", "price": 3.49, "stock": 35},
]

EDITABLE_FIELDS = {"product_name", "brands", "ingredients_text",
                   "barcode", "price", "stock"}


# ---------- helpers ----------
def find_item(item_id):
    return next((i for i in inventory if i["id"] == item_id), None)


def next_id():
    return max((item["id"] for item in inventory), default=0) + 1


def validate_numbers(data):
    """Return an error message if price/stock are invalid, otherwise None."""
    if "price" in data:
        price = data["price"]
        if isinstance(price, bool) or not isinstance(price, (int, float)) or price < 0:
            return "price must be a number >= 0"
    if "stock" in data:
        stock = data["stock"]
        if isinstance(stock, bool) or not isinstance(stock, int) or stock < 0:
            return "stock must be a whole number >= 0"
    return None


def lookup_external(data):
    """Look a product up on OpenFoodFacts by barcode or name.
    Returns (product, error_response); one of the two is always None."""
    try:
        if data.get("barcode"):
            product = fetch_by_barcode(data["barcode"])
        elif data.get("name"):
            product = search_by_name(data["name"])
        else:
            return None, (jsonify({"error": "provide a 'barcode' or 'name'"}), 400)
    except OpenFoodFactsError as exc:
        return None, (jsonify({"error": str(exc)}), 502)

    if product is None:
        return None, (jsonify({"error": "product not found on OpenFoodFacts"}), 404)
    return product, None


# ---------- CRUD routes ----------
@app.get("/inventory")
def get_all():
    return jsonify(inventory), 200


@app.get("/inventory/<int:item_id>")
def get_one(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": "item not found"}), 404
    return jsonify(item), 200


@app.post("/inventory")
def create_item():
    data = request.get_json(silent=True)
    if not data or not data.get("product_name"):
        return jsonify({"error": "product_name is required"}), 400

    problem = validate_numbers(data)
    if problem:
        return jsonify({"error": problem}), 400

    item = {
        "id": next_id(),
        "product_name": data["product_name"],
        "brands": data.get("brands", ""),
        "ingredients_text": data.get("ingredients_text", ""),
        "barcode": data.get("barcode", ""),
        "price": data.get("price", 0),
        "stock": data.get("stock", 0),
    }
    inventory.append(item)
    return jsonify(item), 201


@app.patch("/inventory/<int:item_id>")
def update_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": "item not found"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "no data provided"}), 400

    unknown = set(data) - EDITABLE_FIELDS
    if unknown:
        return jsonify({"error": f"cannot update: {', '.join(sorted(unknown))}"}), 400

    problem = validate_numbers(data)
    if problem:
        return jsonify({"error": problem}), 400

    item.update(data)
    return jsonify(item), 200


@app.delete("/inventory/<int:item_id>")
def delete_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": "item not found"}), 404

    inventory.remove(item)
    return jsonify({"message": "item deleted", "item": item}), 200


# ---------- helper routes (OpenFoodFacts) ----------
@app.get("/lookup")
def lookup():
    """Preview a product from OpenFoodFacts without saving it."""
    product, err = lookup_external(request.args)
    if err:
        return err
    return jsonify(product), 200


@app.post("/inventory/import")
def import_item():
    """Fetch a product from OpenFoodFacts and add it to the inventory."""
    data = request.get_json(silent=True) or {}
    product, err = lookup_external(data)
    if err:
        return err

    extra = {k: data[k] for k in ("price", "stock") if k in data}
    problem = validate_numbers(extra)
    if problem:
        return jsonify({"error": problem}), 400

    item = {
        "id": next_id(),
        **product,
        "price": extra.get("price", 0),
        "stock": extra.get("stock", 0),
    }
    inventory.append(item)
    return jsonify(item), 201


if __name__ == "__main__":
    app.run(debug=True)