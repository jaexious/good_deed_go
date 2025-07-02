import os
import uuid
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
from app import app, db
from models import User, Challenge, Submission, Achievement
from gemini import verify_challenge_completion
import logging

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_current_user():
    """Get current user from session or create anonymous user"""
    if 'user_id' not in session:
        # Create anonymous user for demo purposes
        username = f"user_{uuid.uuid4().hex[:8]}"
        user = User(username=username, email=f"{username}@gooddeedgo.app")
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        session['username'] = user.username
        logging.info(f"Created new user: {username}")
    
    return User.query.get(session['user_id'])

@app.route('/')
def index():
    user = get_current_user()
    recent_challenges = Challenge.query.filter_by(is_active=True).limit(3).all()
    user_submissions = Submission.query.filter_by(user_id=user.id).order_by(Submission.submitted_at.desc()).limit(3).all()
    
    return render_template('index.html', 
                         user=user, 
                         recent_challenges=recent_challenges,
                         user_submissions=user_submissions)

@app.route('/challenges')
def challenges():
    user = get_current_user()
    category = request.args.get('category', 'all')
    
    if category == 'all':
        challenges = Challenge.query.filter_by(is_active=True).all()
    else:
        challenges = Challenge.query.filter_by(is_active=True, category=category).all()
    
    categories = ['all', 'recycling', 'community', 'environment', 'transport']
    
    return render_template('challenges.html', 
                         user=user, 
                         challenges=challenges, 
                         categories=categories,
                         selected_category=category)

@app.route('/challenge/<int:challenge_id>', methods=['GET', 'POST'])
def challenge_detail(challenge_id):
    user = get_current_user()
    challenge = Challenge.query.get_or_404(challenge_id)
    
    # Check if user has already completed this challenge
    existing_submission = Submission.query.filter_by(
        user_id=user.id, 
        challenge_id=challenge_id,
        status='verified'
    ).first()
    
    if request.method == 'GET':
        return render_template('challenge_detail.html', 
                             user=user, 
                             challenge=challenge,
                             completed=existing_submission is not None)
    
    # Handle POST submission
    return submit_challenge_logic(challenge_id, user, challenge)

def submit_challenge_logic(challenge_id, user, challenge):
    user = get_current_user()
    challenge = Challenge.query.get_or_404(challenge_id)
    
    # Check if user has already completed this challenge
    existing_submission = Submission.query.filter_by(
        user_id=user.id, 
        challenge_id=challenge_id,
        status='verified'
    ).first()
    
    if existing_submission:
        return jsonify({'success': False, 'message': 'You have already completed this challenge!'})
    
    # Get location data
    user_lat = float(request.form.get('user_lat', 0))
    user_lng = float(request.form.get('user_lng', 0))
    
    # Handle file upload
    if 'photo' not in request.files:
        return jsonify({'success': False, 'message': 'No photo uploaded!'})
    
    file = request.files['photo']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No photo selected!'})
    
    if file and allowed_file(file.filename):
        # Create unique filename
        filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Ensure upload directory exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Save and resize image
        file.save(filepath)
        try:
            with Image.open(filepath) as img:
                # Resize if too large
                if img.width > 1024 or img.height > 1024:
                    img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
                    img.save(filepath, optimize=True, quality=85)
        except Exception as e:
            logging.error(f"Error processing image: {e}")
        
        # Create submission
        submission = Submission(
            user_id=user.id,
            challenge_id=challenge_id,
            image_path=filepath,
            user_location_lat=user_lat,
            user_location_lng=user_lng
        )
        
        # Verify location
        if not submission.verify_location():
            os.remove(filepath)  # Clean up uploaded file
            return jsonify({'success': False, 'message': 'You are too far from the challenge location!'})
        
        # Use AI to verify the challenge completion
        try:
            verification_result = verify_challenge_completion(filepath, challenge.verification_prompt)
            submission.ai_verification_result = verification_result
            
            # Simple verification logic - if AI response contains positive keywords
            positive_keywords = ['yes', 'correct', 'true', 'verified', 'valid', 'appropriate']
            negative_keywords = ['no', 'incorrect', 'false', 'invalid', 'inappropriate', 'not']
            
            verification_lower = verification_result.lower()
            has_positive = any(keyword in verification_lower for keyword in positive_keywords)
            has_negative = any(keyword in verification_lower for keyword in negative_keywords)
            
            if has_positive and not has_negative:
                submission.status = 'verified'
                submission.points_awarded = challenge.points
                submission.verified_at = datetime.utcnow()
                
                # Update user points and level
                user.total_points += challenge.points
                user.update_level()
                
                # Check for achievements
                check_achievements(user)
                
                return jsonify({
                    'success': True,
                    'message': f'Challenge completed! You earned {challenge.points} points!',
                    'points_awarded': challenge.points
                })
            else:
                submission.status = 'rejected'
                return jsonify({
                    'success': False,
                    'message': 'Your submission could not be verified. Please try again with a clearer photo.'
                })
                
        except Exception as e:
            logging.error(f"AI verification failed: {e}")
            submission.ai_verification_result = f"Verification failed: {str(e)}"
            return jsonify({
                'success': False,
                'message': 'Verification failed. Please try again later.'
            })
        
        db.session.add(submission)
        db.session.commit()
        
        return jsonify({'success': True, 'redirect': url_for('profile')})
    
    return jsonify({'success': False, 'message': 'Invalid file type. Please upload a valid image.'})

def check_achievements(user):
    """Check and award achievements to user"""
    achievements_to_award = []
    
    # First completion achievement
    if user.total_points >= 10 and not Achievement.query.filter_by(user_id=user.id, title='First Steps').first():
        achievements_to_award.append({
            'title': 'First Steps',
            'description': 'Completed your first challenge!',
            'badge_icon': 'fas fa-baby'
        })
    
    # Point milestones
    if user.total_points >= 50 and not Achievement.query.filter_by(user_id=user.id, title='Getting Started').first():
        achievements_to_award.append({
            'title': 'Getting Started',
            'description': 'Earned 50 points!',
            'badge_icon': 'fas fa-star'
        })
    
    if user.total_points >= 100 and not Achievement.query.filter_by(user_id=user.id, title='Century Club').first():
        achievements_to_award.append({
            'title': 'Century Club',
            'description': 'Earned 100 points!',
            'badge_icon': 'fas fa-trophy'
        })
    
    # Category-specific achievements
    recycling_count = Submission.query.join(Challenge).filter(
        Submission.user_id == user.id,
        Submission.status == 'verified',
        Challenge.category == 'recycling'
    ).count()
    
    if recycling_count >= 3 and not Achievement.query.filter_by(user_id=user.id, title='Recycling Hero').first():
        achievements_to_award.append({
            'title': 'Recycling Hero',
            'description': 'Completed 3 recycling challenges!',
            'badge_icon': 'fas fa-recycle'
        })
    
    # Award new achievements
    for achievement_data in achievements_to_award:
        achievement = Achievement(user_id=user.id, **achievement_data)
        db.session.add(achievement)
    
    if achievements_to_award:
        db.session.commit()

@app.route('/profile')
def profile():
    user = get_current_user()
    submissions = Submission.query.filter_by(user_id=user.id).order_by(Submission.submitted_at.desc()).all()
    achievements = Achievement.query.filter_by(user_id=user.id).order_by(Achievement.earned_at.desc()).all()
    
    return render_template('profile.html', 
                         user=user, 
                         submissions=submissions,
                         achievements=achievements)

@app.route('/leaderboard')
def leaderboard():
    user = get_current_user()
    top_users = User.query.filter(User.total_points > 0).order_by(User.total_points.desc()).limit(20).all()
    
    return render_template('leaderboard.html', 
                         user=user, 
                         top_users=top_users)

@app.route('/api/challenges/nearby')
def nearby_challenges():
    """API endpoint for getting challenges near a location"""
    lat = float(request.args.get('lat', 0))
    lng = float(request.args.get('lng', 0))
    
    # For simplicity, return all active challenges with distance calculation on frontend
    challenges = Challenge.query.filter_by(is_active=True).all()
    
    challenge_data = []
    for challenge in challenges:
        challenge_data.append({
            'id': challenge.id,
            'title': challenge.title,
            'description': challenge.description,
            'category': challenge.category,
            'points': challenge.points,
            'latitude': challenge.latitude,
            'longitude': challenge.longitude,
            'completions': challenge.get_completion_count()
        })
    
    return jsonify(challenge_data)
