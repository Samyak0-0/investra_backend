from flask import Blueprint
from routes.stocks import stocks_bp
from routes.sign_up import sign_up_bp

# Registers /api route parent blueprint
# all child routes must be in this directory with name route.py for /api/route/
# sub routes can be defined within the route.py

blueprints = [stocks_bp, sign_up_bp]
api_bp = Blueprint('api', __name__, url_prefix='/api')

for bp in blueprints:
    api_bp.register_blueprint(bp)
