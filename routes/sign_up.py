from flask import Blueprint, request

# Registers /api route parent blueprint
# all child routes must be in this directory with name route.py for /api/route/
# sub routes can be defined within the route.py

sign_up_bp = Blueprint('sign-up', __name__, url_prefix='/sign-up')


@sign_up_bp.route('/', methods=["POST"])
def sign_up():
    data request.get_json()
    data = req.get_json()
    username = data["username"]
    password = data["password"]
    print(username, password)
