from flask import Blueprint, request, jsonify
from db_models import Item, db
import requests, re

api_bp = Blueprint("api", __name__)


# --------------------------
# Helper function to parse package quantity
# --------------------------
def parse_pack_quantity(qty_str):
    if not qty_str:
        return 1, "Stück"
    match = re.match(r"([\d,\.]+)\s*(g|kg|ml|l|Stück|stk)?", qty_str, re.IGNORECASE)
    if match:
        value = float(match.group(1).replace(",", "."))
        unit = match.group(2) if match.group(2) else "Stück"
        if unit.lower() == "kg":
            value *= 1000
            unit = "g"
        if unit.lower() == "l":
            value *= 1000
            unit = "ml"
        return value, unit
    return 1, "Stück"


# --------------------------
# Add item endpoint
# --------------------------
@api_bp.route("/add", methods=["POST"])
def add_item():
    data = request.get_json()
    barcode = data.get("id")
    add_packs = int(data.get("quantity", 1))
    shelf = data.get("shelf", None)

    if not barcode:
        return jsonify({"success": False, "error": "Barcode required"}), 400

    item = Item.query.get(barcode)
    if item:
        item.num_packs += add_packs
        item.quantity = item.num_packs * item.pack_quantity
        if shelf:
            item.shelf = shelf
        db.session.commit()
        return jsonify(
            {
                "success": True,
                "id": barcode,
                "name": item.name,
                "brand": item.brand,
                "quantity": item.quantity,
                "pack_quantity": item.pack_quantity,
                "unit": item.unit,
                "num_packs": item.num_packs,
                "shelf": item.shelf,
                "keywords": item.keywords,
            }
        )

    # Fetch from Open Food Facts if new
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    r = requests.get(url)
    data_api = r.json()
    if data_api.get("status") == 1:
        product = data_api["product"]
        name = product.get("product_name", "Unknown Product")
        brand = product.get("brands", None)
        pack_str = product.get("quantity", None)
        pack_quantity, unit = parse_pack_quantity(pack_str)
        tags = product.get("categories_tags", []) + product.get("labels_tags", [])
        keywords = ",".join(tags) if tags else ""
    else:
        name = "Unknown Product"
        brand = None
        pack_quantity, unit = 1, "Stück"
        keywords = ""

    total_quantity = pack_quantity * add_packs
    item = Item(
        id=barcode,
        name=name,
        brand=brand,
        quantity=total_quantity,
        pack_quantity=pack_quantity,
        unit=unit,
        num_packs=add_packs,
        keywords=keywords,
        shelf=shelf,
    )
    db.session.add(item)
    db.session.commit()

    return jsonify(
        {
            "success": True,
            "id": barcode,
            "name": name,
            "brand": brand,
            "quantity": total_quantity,
            "pack_quantity": pack_quantity,
            "unit": unit,
            "num_packs": add_packs,
            "shelf": shelf,
            "keywords": keywords,
        }
    )


# --------------------------
# Delete item endpoint
# --------------------------
@api_bp.route("/delete", methods=["POST"])
def delete_item():
    data = request.get_json()
    barcode = data.get("id")
    packs = data.get("packs", None)
    quantity = data.get("quantity", None)

    if not barcode:
        return jsonify({"success": False, "error": "Barcode required"}), 400

    item = Item.query.get(barcode)
    if not item:
        return jsonify({"success": False, "error": "Item not found"}), 404

    deleted = False
    if packs:
        packs = int(packs)
        item.num_packs -= packs
        if item.num_packs <= 0:
            db.session.delete(item)
            deleted = True
        else:
            item.quantity = item.num_packs * item.pack_quantity
    elif quantity:
        quantity = float(quantity)
        item.quantity -= quantity
        item.num_packs = max(1, int(item.quantity / item.pack_quantity))
        if item.quantity <= 0:
            db.session.delete(item)
            deleted = True
    else:
        db.session.delete(item)
        deleted = True

    db.session.commit()
    return jsonify(
        {
            "success": True,
            "deleted": deleted,
            "id": item.id if not deleted else barcode,
            "name": item.name if not deleted else None,
            "brand": item.brand if not deleted else None,
            "quantity": item.quantity if not deleted else 0,
            "pack_quantity": item.pack_quantity if not deleted else 0,
            "unit": item.unit if not deleted else None,
            "num_packs": item.num_packs if not deleted else 0,
            "shelf": item.shelf if not deleted else None,
            "keywords": item.keywords if not deleted else None,
        }
    )


# --------------------------
# List all items
# --------------------------
@api_bp.route("/list", methods=["GET"])
def list_items():
    items = Item.query.all()
    return jsonify(
        [
            {
                "id": i.id,
                "name": i.name,
                "brand": i.brand,
                "quantity": i.quantity,
                "pack_quantity": i.pack_quantity,
                "unit": i.unit,
                "num_packs": i.num_packs,
                "shelf": i.shelf,
                "keywords": i.keywords,
            }
            for i in items
        ]
    )


# --------------------------
# Get single item
# --------------------------
@api_bp.route("/item/<barcode>", methods=["GET"])
def get_item(barcode):
    item = Item.query.get(barcode)
    if not item:
        return jsonify({"success": False, "error": "Item not found"}), 404
    return jsonify(
        {
            "id": item.id,
            "name": item.name,
            "brand": item.brand,
            "quantity": item.quantity,
            "pack_quantity": item.pack_quantity,
            "unit": item.unit,
            "num_packs": item.num_packs,
            "shelf": item.shelf,
            "keywords": item.keywords,
        }
    )
