from flask import Blueprint, request, jsonify
from app.models.user import User
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app.auth.oauth import oauth_bp

auth_bp = Blueprint('auth', __name__)
auth_bp.register_blueprint(oauth_bp, url_prefix='/oauth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not all(k in data for k in ('email', 'password')):
        return jsonify({'error': 'Missing required fields'}), 400
        
    if User.find_by_email(data['email']):
        return jsonify({'error': 'Email already registered'}), 400
        
    user = User(
        email=data['email'],
        password=generate_password_hash(data['password']),
        preferences={},
        platforms={}
    )
    user.save()
    
    return jsonify({'message': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not all(k in data for k in ('email', 'password')):
        return jsonify({'error': 'Missing required fields'}), 400
        
    user = User.find_by_email(data['email'])
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
        
    login_user(user)
    return jsonify({'message': 'Logged in successfully'}), 200

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200