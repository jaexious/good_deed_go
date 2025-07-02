from app import db
from datetime import datetime
from sqlalchemy import func

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    total_points = db.Column(db.Integer, default=0)
    level = db.Column(db.String(20), default='Bronze')  # Bronze, Silver, Gold
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    submissions = db.relationship('Submission', backref='user', lazy=True)
    
    def update_level(self):
        """Update user level based on total points"""
        if self.total_points >= 200:
            self.level = 'Gold'
        elif self.total_points >= 100:
            self.level = 'Silver'
        else:
            self.level = 'Bronze'
    
    def get_rank(self):
        """Get user's rank among all users"""
        users_above = User.query.filter(User.total_points > self.total_points).count()
        return users_above + 1

class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # recycling, community, environment, transport
    points = db.Column(db.Integer, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    verification_prompt = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    submissions = db.relationship('Submission', backref='challenge', lazy=True)
    
    def get_completion_count(self):
        """Get number of verified completions"""
        return Submission.query.filter_by(challenge_id=self.id, status='verified').count()

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)
    image_path = db.Column(db.String(200), nullable=False)
    user_location_lat = db.Column(db.Float, nullable=False)
    user_location_lng = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, verified, rejected
    ai_verification_result = db.Column(db.Text)
    points_awarded = db.Column(db.Integer, default=0)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    verified_at = db.Column(db.DateTime)
    
    def verify_location(self, max_distance_km=1.0):
        """Check if user was within acceptable distance of challenge location"""
        from math import radians, cos, sin, asin, sqrt
        
        # Haversine formula to calculate distance between two points on Earth
        challenge_lat = radians(self.challenge.latitude)
        challenge_lng = radians(self.challenge.longitude)
        user_lat = radians(self.user_location_lat)
        user_lng = radians(self.user_location_lng)
        
        dlng = user_lng - challenge_lng
        dlat = user_lat - challenge_lat
        a = sin(dlat/2)**2 + cos(challenge_lat) * cos(user_lat) * sin(dlng/2)**2
        c = 2 * asin(sqrt(a))
        distance_km = 6371 * c  # Radius of earth in kilometers
        
        return distance_km <= max_distance_km

class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    badge_icon = db.Column(db.String(50), nullable=False)  # Font Awesome icon class
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='achievements')
