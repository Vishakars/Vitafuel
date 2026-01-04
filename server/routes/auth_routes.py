from datetime import datetime, timedelta
from typing import Any, Dict

from flask import Blueprint, request, jsonify, current_app
from jose import jwt
from werkzeug.security import generate_password_hash, check_password_hash

from database import db

try:
    # If your project exposes settings at config.settings
    from config.settings import settings
except Exception:
    # Fallback to settings.py at project root if needed
    from settings import settings # type: ignore

auth_bp = Blueprint('auth_bp', __name__)

# Token settings (keep in sync with your decoder in security.py)
ACCESS_TOKEN_EXPIRE_MINUTES = 60 # adjust as needed

def create_access_token(subject: str, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    """
    Create a JWT with sub=email/username and exp. Uses the same SECRET_KEY and
    ALGORITHM as the decoder in security.py.
    """
    to_encode: Dict[str, Any] = {
        "sub": subject,
        "exp": datetime.utcnow() + timedelta(minutes=expires_minutes),
    }
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({'message': 'Name, email and password are required.'}), 400

    if db.users.find_one({'email': email.lower()}):
        return jsonify({'message': 'Email already exists.'}), 409

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    db.users.insert_one({
        'name': name,
        'email': email.lower(),
        'username': email.lower(),  # Use email as username for compatibility
        'password': hashed_password,
        'is_active': True,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    })

    return jsonify({'message': 'User registered successfully!'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 401

    user = db.users.find_one({'email': email.lower()})

    if not user or not check_password_hash(user['password'], password):
        return jsonify({'message': 'Invalid email or password'}), 401

    # Create JWT with "sub" so the decoder can read the current user email/username
    token = create_access_token(subject=str(user['email']))

    # Return a consistent shape used by the frontend
    return jsonify({'access_token': token, 'token_type': 'bearer'}), 200

@auth_bp.route('/update-details', methods=['POST'])
def update_details():
    """
    Endpoint to add additional profile details after initial registration.
    This is an unprotected route, so it relies on the username (email)
    to identify the user to be updated.
    """
    data = request.get_json(silent=True) or {}
    username = data.get('username') # The user's email

    if not username:
        return jsonify({'message': 'Username is required to update details'}), 400

    # Collect any profile details sent from the form
    profile_details = {
        'dob': data.get('dob'),
        'gender': data.get('gender'),
        'height': data.get('height'),
        'weight': data.get('weight')
        # Add any other fields from your register1.html form here
    }

    # Filter out any empty values
    update_data = {k: v for k, v in profile_details.items() if v is not None and v != ""}

    if not update_data:
        return jsonify({'message': 'No details provided'}), 400

    # Find the user and update their document with the new details
    result = db.users.update_one(
        {'username': username},
        {'$set': update_data}
    )

    if result.matched_count == 0:
        return jsonify({'message': 'User not found'}), 404

    return jsonify({'message': 'Profile details added successfully!'}), 200

@auth_bp.route('/complete-profile', methods=['POST'])
def complete_profile():
    """
    Endpoint to add the full, multi-step profile data after initial registration.
    This is an unprotected route that uses the user's email to find the correct document to update.
    """
    data = request.get_json(silent=True) or {}
    email = data.get('email')

    if not email:
        return jsonify({'message': 'Email is required to update profile'}), 400

    # Create a 'profile' object from the data sent by the frontend
    profile_data = {
        'demographics': data.get('demographics', {}),
        'goals': data.get('goals', {}),
        'healthDomains': data.get('healthDomains', []),
        'activities': data.get('activities', []),
        'weeklyGoal': data.get('weeklyGoal', ''),
        'medical': data.get('medical', {}),
        'lifestyle': data.get('lifestyle', {}),
        'preferences': data.get('preferences', {})
    }

    # Also update the user's top-level 'name' field for easy access
    first_name = profile_data.get('demographics', {}).get('firstName', '')
    last_name = profile_data.get('demographics', {}).get('lastName', '')
    full_name = f"{first_name} {last_name}".strip()

    # Prepare the final data to be saved to MongoDB
    update_payload: Dict[str, Any] = {'profile': profile_data}
    if full_name:
        update_payload['name'] = full_name

    # Find the user by their email (which is their 'username') and set the profile data
    result = db.users.update_one(
        {'username': email},
        {'$set': update_payload}
    )

    if result.matched_count == 0:
        return jsonify({'message': 'User to update was not found'}), 404

    return jsonify({'message': 'Profile completed successfully!'}), 200