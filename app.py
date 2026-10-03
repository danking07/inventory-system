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


if __name__ == "__main__":
    app.run(debug=True)