class User(db.Model):
    total_points = db.Column(db.Integer, default=0)
    level = db.Column(db.String(20), default='Bronze')  # Bronze, Silver, Gold
    
    def update_level(self):
        if self.total_points >= 200: self.level = 'Gold'
        elif self.total_points >= 100: self.level = 'Silver'

class Challenge(db.Model):
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    verification_prompt = db.Column(db.Text, nullable=False)

class Submission(db.Model):
    def verify_location(self, max_distance_km=1.0):
        # Haversine formula for GPS distance calculation
        from math import radians, cos, sin, asin, sqrt
        # ... distance calculation code
