from flask import Flask

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pantry.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Import models and routes
from db_models import Item, db
from routes.api import api_bp
from routes.views import views_bp

db.init_app(app)

# Register blueprints
app.register_blueprint(api_bp)
app.register_blueprint(views_bp)

# Initialize database
with app.app_context():
    db.create_all()

# Run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
