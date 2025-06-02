from flask import Flask,  request
from routes.api import api_bp
from dotenv import load_dotenv
from flask_cors import CORS
from models.schemas import User


app = Flask(__name__)
CORS(app)
load_dotenv()


app.register_blueprint(api_bp)

if __name__ == '__main__':
    app.run(debug=True)
