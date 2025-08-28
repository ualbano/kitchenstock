from flask_sqlalchemy import SQLAlchemy

# --------------------------
# Shared database object
# --------------------------
db = SQLAlchemy()


class Item(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(100), nullable=True)
    quantity = db.Column(db.Float, nullable=False)
    pack_quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(10), nullable=True)
    num_packs = db.Column(db.Integer, nullable=False)
    keywords = db.Column(db.Text, nullable=True)
    min_quantity = db.Column(db.Float, nullable=True)
    shelf = db.Column(db.String(50), nullable=True)
