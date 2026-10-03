from flask import Flask, jsonify, request

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


# ---------- helpers ----------
def find_item(item_id):
    return next((i for i in inventory if i["id"] == item_id), None)


def next_id():
    return max((item["id"] for item in inventory), default=0) + 1


# ---------- routes ----------
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


if __name__ == "__main__":
    app.run(debug=True)