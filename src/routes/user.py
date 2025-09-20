from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt,
    get_jwt_identity,
)
from datetime import datetime
from sqlalchemy.exc import IntegrityError
import bcrypt

from src.models.user import db, User, TokenBlocklist

user_bp = Blueprint('user', __name__)


@user_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'error': 'username, email and password are required'}), 400

    if len(password) < 8:
        return jsonify({'error': 'password must be at least 8 characters'}), 400

    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    user = User(username=username, email=email, password_hash=password_hash)
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'user already exists'}), 409

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    return jsonify({
        'message': 'User created successfully',
        'user': {'id': user.id, 'username': user.username, 'email': user.email},
        'access_token': access_token,
        'refresh_token': refresh_token,
    }), 201


@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'invalid credentials'}), 401

    if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        return jsonify({'error': 'invalid credentials'}), 401

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    return jsonify({
        'message': 'Login successful',
        'user': {'id': user.id, 'username': user.username, 'email': user.email},
        'access_token': access_token,
        'refresh_token': refresh_token,
    }), 200


@user_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    return jsonify({'access_token': access_token}), 200


@user_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt().get('jti')
    if not jti:
        return jsonify({'error': 'invalid token'}), 400
    db.session.add(TokenBlocklist(jti=jti, created_at=datetime.utcnow()))
    db.session.commit()
    return jsonify({'message': 'Token revoked'}), 200


@user_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({'error': 'user not found'}), 404
    return jsonify({'id': user.id, 'username': user.username, 'email': user.email}), 200
