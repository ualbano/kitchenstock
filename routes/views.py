from flask import Blueprint, render_template
from db_models import Item

views_bp = Blueprint("views", __name__)


# --------------------------
# Inventory Table View
# --------------------------
@views_bp.route("/items")
def view_items():
    items = Item.query.all()
    return render_template("items.html", items=items)


# --------------------------
# Add Item View
# --------------------------
@views_bp.route("/addview")
def add_view():
    return render_template("add.html")


# --------------------------
# Delete Item View
# --------------------------
@views_bp.route("/deleteview")
def delete_view():
    return render_template("delete.html")
