# routes/goal_routes.py

from flask import Blueprint, request, jsonify
from database import db
from utils.auth_utils import token_required
from bson import ObjectId

goal_bp = Blueprint('goal_bp', __name__)

@goal_bp.route('/', methods=['POST'])
@token_required
def create_goal(current_user_id):
    """
    Creates a new goal for the authenticated user.
    Expects 'healthDomain', 'targetValue', and 'timeframe' in the JSON body.
    """
    data = request.get_json()
    if not data or 'healthDomain' not in data or 'targetValue' not in data:
        return jsonify({'message': 'Missing required goal fields'}), 400

    new_goal = {
        "userId": ObjectId(current_user_id),
        "healthDomain": data['healthDomain'],
        "targetValue": data['targetValue'],
        "timeframe": data.get('timeframe', 'daily') # Default to 'daily'
    }
    
    # Optional: Use upsert to create or update a goal for a specific domain
    db.goals.update_one(
        {"userId": ObjectId(current_user_id), "healthDomain": data['healthDomain']},
        {"$set": new_goal},
        upsert=True
    )

    return jsonify({'message': 'Goal set successfully'}), 201

@goal_bp.route('/', methods=['GET'])
@token_required
def get_goals(current_user_id):
    """
    Retrieves all goals for the authenticated user.
    """
    goals = list(db.goals.find({"userId": ObjectId(current_user_id)}))
    
    # Convert ObjectId to string for JSON serialization
    for goal in goals:
        goal['_id'] = str(goal['_id'])
        goal['userId'] = str(goal['userId'])

    return jsonify(goals), 200

@goal_bp.route('/<goal_id>', methods=['DELETE'])
@token_required
def delete_goal(current_user_id, goal_id):
    """
    Deletes a specific goal by its ID.
    """
    result = db.goals.delete_one({
        "_id": ObjectId(goal_id),
        "userId": ObjectId(current_user_id) # Ensure user can only delete their own goals
    })

    if result.deleted_count == 0:
        return jsonify({'message': 'Goal not found or user not authorized'}), 404
        
    return jsonify({'message': 'Goal deleted successfully'}), 200
