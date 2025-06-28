import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///gooddeedgo.db")
db = SQLAlchemy(model_class=Base)


default_challenges = [
    {
        'title': 'Recycling Photo',
        'points': 10,
        'latitude': 40.7831,
        'longitude': -73.9712,
        'verification_prompt': 'Is this person taking a photo while recycling?'
    }
]
