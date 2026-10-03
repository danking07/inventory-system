from flask import Flask, jsonify

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


@app.get("/inventory")
def get_all():
    return jsonify(inventory), 200


def find_item(item_id):
    return next((i for i in inventory if i["id"] == item_id), None)


@app.get("/inventory/<int:item_id>")
def get_one(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": "item not found"}), 404
    return jsonify(item), 200

if __name__ == "__main__":
    app.run(debug=True)