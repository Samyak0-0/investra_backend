# signup.py
from flask import Blueprint, request, jsonify
from models.schemas import User
from models.database import engine
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import uuid
import os

signup_bp = Blueprint('signup', __name__)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

@signup_bp.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    token = data.get("token")

    try:
        # Verify the token
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), GOOGLE_CLIENT_ID)
        email = idinfo["email"]
        name = idinfo.get("name", "")
        user_id = idinfo.get("sub", str(uuid.uuid4()))

        with Session(engine) as session:
            existing_user = session.query(User).filter_by(email=email).first()
            if existing_user:
                return jsonify({"message": "User exists", "user_id": existing_user.id})

            new_user = User(id=user_id, email=email, name=name, password_hash=None)
            session.add(new_user)
            session.commit()

            return jsonify({"message": "User created", "user_id": new_user.id})
    except Exception as e:
        return jsonify({"error": "Invalid token", "details": str(e)}), 400
