from flask import Blueprint
from routes.stocks import stocks_bp

from routes.portfolio import portfolio_bp
from routes.comparison import comparison_bp

from routes.stocks.stocks import stocks_bp
from routes.stocks.news import news_bp
from routes.sign_up import sign_up_bp
from routes.simulation import simulation_bp
# from routes.users.user_portfolio import userportfolio_bp

# Registers /api route parent blueprint
# all child routes must be in this directory with name route.py for /api/route/
# sub routes can be defined within the route.py

# blueprints = [stocks_bp, sign_up_bp, userportfolio_bp, portfolio_bp, comparison_bp, simulation_bp]

blueprints = [stocks_bp, sign_up_bp, portfolio_bp, comparison_bp, simulation_bp,news_bp]
api_bp = Blueprint('api', __name__, url_prefix='/api')

for bp in blueprints:
    api_bp.register_blueprint(bp)
