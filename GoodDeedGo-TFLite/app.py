import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure upload folder
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///gooddeedgo.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Import routes after app creation to avoid circular imports
from routes import *

with app.app_context():
    # Import models to ensure tables are created
    import models
    db.create_all()
    
    # Create default challenges if none exist
    if models.Challenge.query.count() == 0:
        default_challenges = [
            {
                'title': 'Recycling Selfie',
                'description': 'Take a selfie while throwing trash in a recycling bin near this park.',
                'category': 'recycling',
                'points': 10,
                'latitude': 40.7831,
                'longitude': -73.9712,
                'verification_prompt': 'Is this person taking a selfie while recycling or near a recycling bin?'
            },
            {
                'title': 'Support Local Women-Led Business',
                'description': 'Find a local women-led business and write a positive review.',
                'category': 'community',
                'points': 15,
                'latitude': 40.7589,
                'longitude': -73.9851,
                'verification_prompt': 'Does this image show someone at or near a local business?'
            },
            {
                'title': 'Climate Awareness Mural',
                'description': 'Visit a mural related to climate awareness and share its story.',
                'category': 'environment',
                'points': 20,
                'latitude': 40.7505,
                'longitude': -73.9934,
                'verification_prompt': 'Does this image show a climate or environmental awareness mural or artwork?'
            },
            {
                'title': 'Community Garden Volunteer',
                'description': 'Help at a community garden and document your contribution.',
                'category': 'environment',
                'points': 25,
                'latitude': 40.7614,
                'longitude': -73.9776,
                'verification_prompt': 'Does this image show someone working in or helping with a community garden?'
            },
            {
                'title': 'Public Transport Check-in',
                'description': 'Use public transportation and share your eco-friendly choice.',
                'category': 'transport',
                'points': 8,
                'latitude': 40.7527,
                'longitude': -73.9772,
                'verification_prompt': 'Does this image show someone using public transportation (bus, subway, train)?'
            }
        ]
        
        for challenge_data in default_challenges:
            challenge = models.Challenge(**challenge_data)
            db.session.add(challenge)
        
        db.session.commit()
        logging.info("Default challenges created")
