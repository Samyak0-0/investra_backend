from flask import Blueprint, jsonify
from routes.stocks import stocks_bp

# Registers /api route parent blueprint 
# all child routes must be in this directory with name route.py for /api/route/
# sub routes can be defined within the route.py

api_bp = Blueprint('api', __name__, url_prefix='/api')
api_bp.register_blueprint(stocks_bp) 
