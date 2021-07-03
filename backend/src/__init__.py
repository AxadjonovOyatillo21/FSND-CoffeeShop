from flask import Flask
from flask_cors import CORS

from .database.models import setup_db, db_drop_and_create_all

app = Flask(__name__)
setup_db(app)
CORS(app)
from. import api