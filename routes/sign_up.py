from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from utils.helpers import registration
import uuid
from models.database import SessionLocal
from models.schemas import User

# Registers /api route parent blueprint
# all child routes must be in this directory with name route.py for /api/route/
# sub routes can be defined within the route.py

sign_up_bp = Blueprint('sign-up', __name__, url_prefix='/sign-up')
bcrypt = Bcrypt()


@sign_up_bp.route('/', methods=["POST"])
def sign_up():
    data = request.get_json()
    username = data["username"]
    email = data["email"]
    password = data["password"]
    repeat_password = data["repeat_password"]

    if password != repeat_password:
        return jsonify({"[ERROR]": "Password donot match!"})

    hashed_password = bcrypt.generate_password_hash(
        data["password"]).decode('utf-8')

    if registration.doesUserExistByUsername(username):
        return jsonify({"[ERROR]": "User already exists!"})

    session = SessionLocal()
    user = User(name=username,password_hash=hashed_password,email=email)
    session.add(user)
    session.commit()
    session.close()
    return jsonify({"[SUCESS]":"Registered!"})
