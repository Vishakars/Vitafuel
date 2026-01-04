# routes/profile_routes.py

from flask import Blueprint, jsonify, request
from functools import wraps
import jwt
import os

# --- This is our new, clean profile route ---
profile_bp = Blueprint('profile_bp', __name__)

# --- This is our token-checking "decorator" ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            # Use the app's secret key for decoding
            secret_key = os.environ.get("SECRET_KEY")
            data = jwt.decode(token, secret_key, algorithms=["HS256"])
            # The user's data (like their username/email) is now in 'data'
            current_user = data
        except Exception as e:
            return jsonify({'message': 'Token is invalid!', 'error': str(e)}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated


# --- Define the Profile Route ---
# The route is '/profile' with NO trailing slash.
@profile_bp.route('/profile', methods=['GET'])
@token_required
def get_user_profile(current_user):
    # 'current_user' is the payload from the decoded JWT token
    # It contains the user's username (email)
    from database import db # Import db here to avoid circular imports
    
    user = db.users.find_one({'username': current_user['username']})
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
        
    # Remove the password hash before sending the data
    if 'password' in user:
        del user['password']
    
    # The user object from MongoDB has an '_id' field that is not JSON serializable
    # We must convert it to a string.
    user['_id'] = str(user['_id'])
    
    return jsonify(user)

