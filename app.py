from flask import Flask,  request
from routes.api import api_bp
from dotenv import load_dotenv
from flask_cors import CORS
from models.schemas import User


app = Flask(__name__)
CORS(app)
load_dotenv()


@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data["username"]
    password = data["password"]

    user = User.query.filter_by(username=username).first()
    return user


app.register_blueprint(api_bp)

if __name__ == '__main__':
    app.run(debug=True)
