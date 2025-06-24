from flask import Blueprint, jsonify
from flask import request
import os
import json
from models.schemas import User, Portfolio
from models.database import engine
from sqlalchemy.orm import sessionmaker

portfolio_bp = Blueprint('portfolio', __name__, url_prefix='/portfolio')

@portfolio_bp.route('/', methods=['GET'])
def get_portfolio():
    
    mail = request.args.get('mail')
    print(mail)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    user = session.query(User).filter_by(email=mail).first()
    if user:
        portfolios = session.query(Portfolio).filter_by(user_id=user.id).all()
        session.close()
        print(user.name)
        return jsonify({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "portfolio": [
                {
                    "stock_name": p.stock_name,
                    "stock_amt": p.stock_amt,
                    "added_at": str(p.added_at)
                } for p in portfolios
            ]
        })
    else:
        session.close()
        return jsonify({"error": "User not found"}), 404
