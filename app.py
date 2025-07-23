from dotenv import load_dotenv
load_dotenv()  #load .env FIRST before importing anything else

from flask import Flask
from flask_cors import CORS
from routes.api import api_bp

from models.schemas import User
import os

from models.database import engine as db
from models.database import Base

app = Flask(__name__)
CORS(app)

app.register_blueprint(api_bp)

if __name__ == '__main__':
    Base.metadata.create_all(db)
    app.run(debug=True)
