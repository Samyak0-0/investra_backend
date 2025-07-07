from flask import Blueprint, jsonify, request
import datetime
from utils.helpers.stocks import stockSymbolToId
from models.schemas import Portfolio, Stocks
from models.database import SessionLocal

userportfolio_bp = Blueprint('userPortfolio', __name__,
                             url_prefix="/user/portfolio")

# Add a stock to user's portfolio


@userportfolio_bp.route('/add/<symbol>', methods=["PUT"])
def add_stock_choice(symbol):
    try:
        user_id = request.json.get('user_id')
        stock_quantity = request.json.get('quantity')
        if not user_id:
            return jsonify({"error": "Missing user_id"}), 400

        stock_id = stockSymbolToId(symbol)
        session = SessionLocal()
        portfolio = session.query(Portfolio).filter_by(
            user_id=user_id, stock_id=stock_id).first()
        if (portfolio):
            portfolio.quantity = stock_quantity
            portfolio.updated_at = datetime.datetime.now()
        else:
            new_entry = Portfolio(
                user_id=user_id, stock_id=stock_id, quantity=stock_quantity)
            session.add(new_entry)

        session.commit()
        session.close()
        return jsonify({"message": f"Added {symbol} to portfolio."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Remove a stock from user's portfolio


@userportfolio_bp.route('/remove/<symbol>', methods=["DELETE"])
def remove_stock_choice(symbol):
    try:
        user_id = request.json.get('user_id')
        symbol_name = symbol
        if not user_id:
            return jsonify({"error": "Missing user_id"}), 400

        session = SessionLocal()
        result = stockSymbolToId(symbol_name)
        if not result:
            return jsonify({"error": "Missing/Malformed stock symbol"}, 404)
        item = session.query(Portfolio).filter_by(
            user_id=user_id, stock_id=result).first()
        if not item:
            return jsonify({"error": "Stock not found in portfolio"}), 404

        session.delete(item)
        session.commit()
        session.close()
        return jsonify({"message": f"Removed {symbol} from portfolio."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@userportfolio_bp.route('/', methods=["POST"])
def get_stocks_user():
    try:
        user_id = request.json.get('user_id')
        session = SessionLocal()
        portfolio_stock = session.query(Portfolio, Stocks).join(
            Stocks, Portfolio.stock_id == Stocks.id).filter(Portfolio.user_id == user_id).all()
        if portfolio_stock:
            result = [
                s.to_dict() | p.to_dict()
                for p, s in portfolio_stock
            ]
            return jsonify(result), 200
        else:
            return jsonify({"Status": "Fail"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 499
