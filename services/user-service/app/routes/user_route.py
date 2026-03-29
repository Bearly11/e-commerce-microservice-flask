from flask import Blueprint, request, jsonify
from ..services.user_service import UserService
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (create_access_token,
                                create_refresh_token,jwt_required,
                                get_jwt_identity,get_jwt,decode_token)

user_bp = Blueprint('user_bp', __name__)


@user_bp.route('/', methods=['GET'])
def list_users():
    users = UserService.get_all_users()
    return jsonify({'message': 'Users retrieved',
                    'users': [{'id': u.id, 'name': u.name, 'email': u.email} for u in users]}), 200


@user_bp.route('/', methods=['POST'])
def add_user():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({'error': 'Name, email, and password are required'}), 400

    if UserService.get_user_by_email(email):
        return jsonify({'error': 'Email already exists'}), 400

    password_hash = generate_password_hash(password)
    new_user = UserService.create_user(name, email, password_hash)
    return jsonify({'message': 'User created',
                    'user': {'id': new_user.id, 'name': new_user.name, 'email': new_user.email}}), 201


@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = UserService.get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'id': user.id, 'name': user.name, 'email': user.email}), 200


@user_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if email and UserService.get_user_by_email(email) and UserService.get_user_by_email(email).id != user_id:
        return jsonify({'error': 'Email already exists'}), 400

    password_hash = generate_password_hash(password) if password else None
    updated_user = UserService.update_user(user_id, name, email, password_hash)
    if not updated_user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'message': 'User updated',
                    'user': {'id': updated_user.id,
                             'name': updated_user.name, 'email': updated_user.email}}), 200


@user_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    if not UserService.delete_user(user_id):
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'message': 'User deleted'}), 200


@user_bp.route('/<int:user_id>/reset_password', methods=['POST'])
def reset_password(user_id):
    data = request.get_json()
    new_password = data.get('new_password')

    if not new_password:
        return jsonify({'error': 'New password is required'}), 400

    new_password_hash = generate_password_hash(new_password)
    updated_user = UserService.reset_password(user_id, new_password_hash)
    if not updated_user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'message': 'Password reset successful',
                    'user': {'id': updated_user.id,
                             'name': updated_user.name,
                             'email': updated_user.email}}), 200


@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = UserService.get_user_by_email(email)

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid email or password'}), 401

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    UserService.create_refresh_token(user.id, refresh_token)
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'refresh_token':refresh_token}), 200

#####################
# pending user routes
######################

@user_bp.route('/register', methods=['POST'])
def create_pending_user():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({'error': 'Name, email, and password are required'}), 400

    if not UserService.is_valid_email(email):
        return jsonify({'error': 'Invalid email format'}), 400

    if not UserService.is_strong_password(password):
        return jsonify({
            'error':
            'Password must be at least 8 characters long and include uppercase,'
            ' lowercase, number, and special character'}), 400

    if UserService.get_user_by_email(email):
        return jsonify({'error': 'Email already exists'}), 400

    password_hash = generate_password_hash(password)
    try:
        pending_user = UserService.create_pending_user(name, email, password_hash)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    try:
        token = UserService.get_token_by_email(email)
    except Exception as e:
        return jsonify({'error': 'Failed to generate verification token'}), 500

    try:
        UserService.send_verification_email(email, token)
    except Exception as e:
        return jsonify({'error': 'Failed to send verification email',

                    }), 500
    access_token = create_access_token(identity=email)

    return jsonify({'message': 'Pending user created',
                    'pending_user': {'id': pending_user.id,
                                     'name': pending_user.name,
                                     'email': pending_user.email,
                                     'access_token':access_token}}), 201

@user_bp.route('/verify', methods=['POST'])
def verify_pending_user():
    data = request.get_json()
    email = data.get('email')
    token = data.get('verification_token')
    if not email or not token:
        return jsonify({'error': 'Email and verification token are required'}), 400

    pending_user = UserService.get_pending_user_by_email(email)
    if not pending_user:
        return jsonify({'error': 'Pending user not found'}), 404

    if pending_user.verification_token != token:
        return jsonify({'error': 'Invalid verification token'}), 400


    confirm = UserService.two_factor_authenticate(email, token)
    if not confirm:
        return jsonify({'error': 'Verification failed'}), 400

    return jsonify({
        'message': 'Verification successful. Please log in.'}), 200

####################
#refresh token route
#####################

@user_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    jti = get_jwt()['jti']
    if not UserService.is_refresh_token_valid(user_id, jti):
        return jsonify({'error': 'Invalid or revoke token'}), 401
    success = UserService.revoke_refresh_token(user_id, jti)
    if not success:
        return jsonify({'error': 'Failed to revoke token'}), 500

    new_access_token = create_access_token(identity=user_id)
    new_refresh_token = create_refresh_token(identity=user_id)

    new_jti = decode_token(new_refresh_token)['jti']

    UserService.create_refresh_token(user_id, new_jti)

    return jsonify({
        'access_token': new_access_token,
        'refresh_token': new_refresh_token}), 200

@user_bp.route('/logout', methods=['POST'])
@jwt_required(refresh=True)
def logout():
    user_id = get_jwt_identity()
    token = get_jwt()['jti']
    success=UserService.revoke_refresh_token(user_id,token)
    if not success:
        return jsonify({'error': 'Failed to revoke token'}), 500
    return jsonify({'message': 'Logged out successfully'}), 200
