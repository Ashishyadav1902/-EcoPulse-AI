import os
from flask import Flask, request, jsonify, session, render_template
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from models import db, User, CarbonRecord, Goal, Challenge, Achievement
from ai_engine import get_recommendations, chat_with_ai
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key-for-dev')

# Check if using Supabase Postgres or local SQLite
db_url = os.getenv('DATABASE_URL', 'sqlite:///ecopulse.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app, supports_credentials=True)
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- FRONTEND ROUTE ---
@app.route('/')
def index():
    return render_template('index.html')

# --- AUTHENTICATION API ---
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
        return jsonify({'error': 'User already exists'}), 400
        
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, email=email, password_hash=hashed_password)
    
    db.session.add(new_user)
    db.session.commit()
    
    login_user(new_user)
    return jsonify({'message': 'Registration successful', 'user': new_user.to_dict()}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password_hash, password):
        login_user(user)
        return jsonify({'message': 'Login successful', 'user': user.to_dict()}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    if current_user.is_authenticated:
        return jsonify({'user': current_user.to_dict()}), 200
    return jsonify({'error': 'Not authenticated'}), 401

# --- TRACKING API ---
@app.route('/api/calculate', methods=['POST'])
@login_required
def calculate():
    data = request.get_json()
    
    transport = float(data.get('transport', 0))
    energy = float(data.get('energy', 0))
    food = float(data.get('food', 0))
    waste = float(data.get('waste', 0))
    water = float(data.get('water', 0))
    
    total = transport + energy + food + waste + water
    
    record = CarbonRecord(
        user_id=current_user.id,
        transport_emissions=transport,
        energy_emissions=energy,
        food_emissions=food,
        waste_emissions=waste,
        water_emissions=water,
        total=total
    )
    
    # Update user points and score based on submission
    current_user.points += 10
    current_user.sustainability_score = min(100, max(0, 100 - int(total / 10))) # Simplified score calculation
    
    db.session.add(record)
    db.session.commit()
    
    return jsonify({'message': 'Record added', 'record': record.to_dict()}), 201

@app.route('/api/dashboard', methods=['GET'])
@login_required
def dashboard():
    records = CarbonRecord.query.filter_by(user_id=current_user.id).order_by(CarbonRecord.created_at.desc()).limit(10).all()
    goals = Goal.query.filter_by(user_id=current_user.id).all()
    
    latest_record = records[0] if records else None
    
    return jsonify({
        'user': current_user.to_dict(),
        'recent_records': [r.to_dict() for r in records],
        'goals': [g.to_dict() for g in goals],
        'latest_total': latest_record.total if latest_record else 0
    }), 200

@app.route('/api/recommendations', methods=['GET'])
@login_required
def recommendations():
    latest_record = CarbonRecord.query.filter_by(user_id=current_user.id).order_by(CarbonRecord.created_at.desc()).first()
    if not latest_record:
        return jsonify({'recommendations': ["Start tracking your footprint to receive personalized recommendations."]})
        
    recs = get_recommendations(latest_record)
    return jsonify({'recommendations': recs}), 200

@app.route('/api/user/profile', methods=['GET', 'PUT'])
@login_required
def user_profile():
    if request.method == 'PUT':
        data = request.get_json()
        if 'location_lat' in data and 'location_lon' in data:
            current_user.location_lat = float(data['location_lat'])
            current_user.location_lon = float(data['location_lon'])
            current_user.location_name = data.get('location_name', '')
            db.session.commit()
            return jsonify({'message': 'Location updated successfully', 'user': current_user.to_dict()}), 200
        return jsonify({'error': 'Invalid data'}), 400
        
    return jsonify({'user': current_user.to_dict()}), 200

@app.route('/api/weather', methods=['GET'])
@login_required
def weather():
    if not current_user.location_lat or not current_user.location_lon:
        return jsonify({'error': 'Location not set'}), 400
        
    weather_api_key = os.getenv("WEATHER_API_KEY")
    if not weather_api_key:
        return jsonify({'error': 'Weather API key not configured'}), 500
        
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={current_user.location_lat}&lon={current_user.location_lon}&appid={weather_api_key}&units=metric"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return jsonify(response.json()), 200
        return jsonify({'error': 'Failed to fetch weather'}), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    data = request.get_json()
    message = data.get('message', '')
    if not message:
        return jsonify({'error': 'Message is required'}), 400
        
    latest_record = CarbonRecord.query.filter_by(user_id=current_user.id).order_by(CarbonRecord.created_at.desc()).first()
    context = latest_record.to_dict() if latest_record else None
    
    reply = chat_with_ai(message, context)
    return jsonify({'reply': reply}), 200

@app.route('/api/goals', methods=['POST', 'GET'])
@login_required
def manage_goals():
    if request.method == 'POST':
        data = request.get_json()
        new_goal = Goal(
            user_id=current_user.id,
            title=data.get('title'),
            target=float(data.get('target', 0))
        )
        db.session.add(new_goal)
        db.session.commit()
        return jsonify({'message': 'Goal created', 'goal': new_goal.to_dict()}), 201
        
    goals = Goal.query.filter_by(user_id=current_user.id).all()
    return jsonify({'goals': [g.to_dict() for g in goals]}), 200

@app.route('/api/leaderboard', methods=['GET'])
def leaderboard():
    top_users = User.query.order_by(User.points.desc()).limit(10).all()
    return jsonify({'leaderboard': [{'username': u.username, 'points': u.points, 'level': u.level} for u in top_users]}), 200

# Ensure DB tables are created
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
