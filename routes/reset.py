from flask import Blueprint, jsonify
from flask import request
import requests
import os
import json

reset_bp = Blueprint('reset', __name__, url_prefix='/reset')

@reset_bp.route('/', methods=['DELETE'])
def reset_portfolio():
    userId = request.args.get('userId')
    if not userId:
        return jsonify({"error": "userId is required"}), 400

    appdata_dir = os.path.join(os.path.dirname(__file__), '..', 'appdata', 'userPortfolios')
    filepath = os.path.join(appdata_dir, f"{userId}.json")
    
    if os.path.exists(filepath):
        os.remove(filepath)
        return jsonify({"message": f"Portfolio for user {userId} has been reset."}), 200
    else:
        return jsonify({"error": f"No portfolio found for user {userId}"}), 404

