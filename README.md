# Inventory Manager

A small project for managing a shop's inventory. It has:

- A Flask API to add, view, update and delete products
- A command-line menu to use the API
- A lookup that gets product details from the OpenFoodFacts website

Note: the products are stored in a simple Python list, so the data resets every time the server restarts.

## How to set it up

You need Python and Git installed.

```bash
git clone https://github.com/danking07/inventory-system.git
cd inventory-system
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows, use `.venv\Scripts\activate` instead of the `source` line.

## How to run it

Open two terminals and activate the virtual environment in both.

Terminal 1 starts the API:

```bash
python app.py
```

Terminal 2 starts the menu:

```bash
python cli.py
```

## What the menu can do

1. Show all items
2. Show one item
3. Add an item
4. Update price or stock
5. Delete an item
6. Find a product on OpenFoodFacts (and add it to the inventory)

Example of finding a product:

```
Choose an option: 6
Search by barcode (b) or name (n)? b
Barcode: 3017620422003
Found: Nutella (Nutella, Ferrero)
Add it to the inventory? (y/n): y
Price: 6.5
Stock: 12
Item added!
```

## API endpoints

| Method | Endpoint | What it does |
|--------|----------|--------------|
| GET | `/inventory` | Show all items |
| GET | `/inventory/<id>` | Show one item |
| POST | `/inventory` | Add an item |
| PATCH | `/inventory/<id>` | Change an item |
| DELETE | `/inventory/<id>` | Delete an item |
| GET | `/lookup?barcode=...` or `/lookup?name=...` | Look up a product on OpenFoodFacts |
| POST | `/inventory/import` | Get a product from OpenFoodFacts and add it |

Each item looks like this:

```json
{
  "id": 1,
  "product_name": "Organic Almond Milk",
  "brands": "Silk",
  "ingredients_text": "Filtered water, almonds, cane sugar",
  "barcode": "0025293001213",
  "price": 4.99,
  "stock": 20
}
```

Rules:
- Price must be a number of 0 or more.
- Stock must be a whole number of 0 or more.
- The ID can't be changed.

Example request:

```bash
curl -X POST http://127.0.0.1:5000/inventory \
  -H "Content-Type: application/json" \
  -d '{"product_name": "Oat Milk", "price": 3.99, "stock": 15}'
```

## How to run the tests

```bash
pytest -v
```

The tests use fake responses, so they don't need the internet.

## Files

- `app.py` - the Flask API
- `off_client.py` - gets data from OpenFoodFacts
- `cli.py` - the command-line menu
- `tests/` - the tests
- `requirements.txt` - the libraries needed