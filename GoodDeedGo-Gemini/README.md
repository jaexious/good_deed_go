# Good Deed Go - Environmental Challenge Platform

A location-based environmental challenge app similar to Pokémon Go that uses GPS to give users location-specific mini-missions. Built with Python Flask for high school project presentation.

## Quick Start

### 1. Install Dependencies
```bash
pip install flask flask-sqlalchemy google-genai pillow psycopg2-binary gunicorn werkzeug
```

### 2. Set Environment Variables (Optional)
```bash
export GEMINI_API_KEY="your-gemini-api-key"  # For AI photo verification
export SESSION_SECRET="your-secret-key"      # For production
export DATABASE_URL="sqlite:///gooddeedgo.db" # Database connection
```

### 3. Run the Application
```bash
python main.py
```
or
```bash
gunicorn --bind 0.0.0.0:5000 --reload main:app
```

### 4. Open Browser
Navigate to `http://localhost:5000`

## Features

- **Location-Based Challenges**: GPS-verified environmental tasks
- **AI Photo Verification**: Google Gemini verifies challenge completion
- **Mobile-First Interface**: Responsive design matching UI specifications
- **Gamification**: Points, levels (Bronze/Silver/Gold), achievements
- **Real-Time Map**: Discover nearby environmental opportunities

## Tech Stack

- **Backend**: Python Flask, SQLAlchemy ORM
- **Database**: SQLite (production-ready for PostgreSQL)
- **AI**: Google Gemini 2.5 Flash for image analysis
- **Frontend**: Jinja2 templates, Bootstrap CSS, Vanilla JavaScript
- **Authentication**: Session-based with anonymous user creation

## Project Structure

```
gooddeedgo/
├── app.py              # Flask application setup
├── models.py           # Database models
├── routes.py           # Web routes and API endpoints
├── gemini.py           # AI verification logic
├── main.py             # Application entry point
├── templates/          # HTML templates
│   ├── base.html       # Main layout
│   ├── index.html      # Home page
│   ├── challenges.html # Challenge discovery
│   ├── profile.html    # User profile
│   └── ...
├── static/uploads/     # User photo submissions
└── pyproject.toml      # Dependencies
```

## API Endpoints

- `GET /` - Home page
- `GET /challenges` - Challenge discovery
- `GET|POST /challenge/<id>` - Challenge detail and submission
- `GET /profile` - User profile and achievements
- `GET /leaderboard` - Global rankings

## Database Models

- **User**: Profile, points, level progression
- **Challenge**: Environmental tasks with GPS coordinates
- **Submission**: Photo submissions with AI verification
- **Achievement**: Milestone rewards and badges

## Development Notes

- Built for high school computer science presentation
- 548 lines of Python code demonstrating full-stack development
- Integrates multiple technologies: databases, AI, geolocation, file handling
- Production-ready architecture with proper error handling