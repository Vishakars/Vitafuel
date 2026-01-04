# routes/data_routes.py

from flask import Blueprint, request, jsonify
from database import db
from utils.auth_utils import token_required
# Corrected Import: Added timedelta
from datetime import datetime, time, timedelta 
from bson import ObjectId

data_bp = Blueprint('data_bp', __name__)

@data_bp.route('/', methods=['POST'])
@token_required
def log_data(current_user_id):
    req_data = request.get_json()
    if not req_data or 'healthDomain' not in req_data or 'data' not in req_data:
        return jsonify({'message': 'Missing healthDomain or data field'}), 400

    new_log = {
        "userId": ObjectId(current_user_id),
        "healthDomain": req_data['healthDomain'],
        "data": req_data['data'],
        "timestamp": datetime.utcnow()
    }
    db.health_data.insert_one(new_log)
    return jsonify({'message': 'Data logged successfully!'}), 201

@data_bp.route('/today', methods=['GET'])
@token_required
def get_today_data(current_user_id):
    today_start = datetime.combine(datetime.utcnow().date(), time.min)
    today_end = datetime.combine(datetime.utcnow().date(), time.max)

    query = {
        "userId": ObjectId(current_user_id),
        "timestamp": {"$gte": today_start, "$lte": today_end}
    }
    todays_logs = list(db.health_data.find(query))

    for log in todays_logs:
        log['_id'] = str(log['_id'])
        log['userId'] = str(log['userId'])
    return jsonify(todays_logs), 200

@data_bp.route('/history', methods=['GET'])
@token_required
def get_historical_data(current_user_id):
    period = request.args.get('period', 'weekly')
    end_date = datetime.utcnow()
    if period == 'weekly':
        start_date = end_date - timedelta(days=7)
    elif period == 'monthly':
        start_date = end_date - timedelta(days=30)
    else:
        start_date = datetime.min

    pipeline = [
        {'$match': {'userId': ObjectId(current_user_id), 'timestamp': {'$gte': start_date, '$lte': end_date}}},
        {'$group': {
            '_id': {'domain': '$healthDomain', 'date': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$timestamp'}}},
            'totalValue': {'$sum': '$data.value'}
        }},
        {'$sort': {'_id.date': 1}}
    ]
    aggregated_data = list(db.health_data.aggregate(pipeline))
    
    result = {}
    for item in aggregated_data:
        domain = item['_id']['domain']
        if domain not in result:
            result[domain] = []
        result[domain].append({'date': item['_id']['date'], 'total': item['totalValue']})
    return jsonify(result), 200
