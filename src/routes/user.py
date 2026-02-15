from flask import Blueprint, request, jsonify
from src.models.user import db, User
from flask_jwt_extended import create_access_token

user_bp = Blueprint("user", __name__)


@user_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if (
        not data
        or not data.get("username")
        or not data.get("email")
        or not data.get("password")
    ):
        return jsonify({"error": "Missing required fields"}), 400

    # Vérifier si l'utilisateur existe déjà
    existing_user = User.query.filter_by(email=data["email"]).first()
    if existing_user:
        return jsonify({"error": "User already exists"}), 409

    # Créer un nouvel utilisateur
    new_user = User(username=data["username"], email=data["email"])
    new_user.set_password(data["password"])

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify(
            {"message": "User created successfully", "user_id": new_user.id}
        ), 201
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Database error"}), 500


@user_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password required"}), 400

    user = User.query.filter_by(email=data["email"]).first()

    if user and user.check_password(data["password"]):
        access_token = create_access_token(identity=str(user.id))
        return jsonify(
            {
                "message": "Login successful",
                "user_id": user.id,
                "access_token": access_token,
            }
        ), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401
