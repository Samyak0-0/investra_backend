from flask import Flask
from routes.api import api_bp
from dotenv import load_dotenv
from flask_cors import CORS

from models.schemas import User
import os

from models.database import engine as db
from models.database import Base

app = Flask(__name__) # App instance
CORS(app)
load_dotenv()

app.register_blueprint(api_bp) # Blueprint for /api route

if __name__ == '__main__':
    Base.metadata.create_all(db)
    app.run(debug=True)
