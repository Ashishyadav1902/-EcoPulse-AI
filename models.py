from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'ecopulse_users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    points = db.Column(db.Integer, default=0)
    level = db.Column(db.String(50), default='Seed')
    sustainability_score = db.Column(db.Integer, default=0)
    location_lat = db.Column(db.Float, nullable=True)
    location_lon = db.Column(db.Float, nullable=True)
    location_name = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    records = db.relationship('CarbonRecord', backref='user', lazy=True)
    goals = db.relationship('Goal', backref='user', lazy=True)
    achievements = db.relationship('Achievement', backref='user', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'points': self.points,
            'level': self.level,
            'sustainability_score': self.sustainability_score,
            'location_lat': self.location_lat,
            'location_lon': self.location_lon,
            'location_name': self.location_name,
            'created_at': self.created_at.isoformat()
        }

class CarbonRecord(db.Model):
    __tablename__ = 'ecopulse_carbon_records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('ecopulse_users.id'), nullable=False)
    transport_emissions = db.Column(db.Float, default=0.0)
    energy_emissions = db.Column(db.Float, default=0.0)
    food_emissions = db.Column(db.Float, default=0.0)
    waste_emissions = db.Column(db.Float, default=0.0)
    water_emissions = db.Column(db.Float, default=0.0)
    total = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'transport_emissions': self.transport_emissions,
            'energy_emissions': self.energy_emissions,
            'food_emissions': self.food_emissions,
            'waste_emissions': self.waste_emissions,
            'water_emissions': self.water_emissions,
            'total': self.total,
            'created_at': self.created_at.isoformat()
        }

class Goal(db.Model):
    __tablename__ = 'ecopulse_goals'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('ecopulse_users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    target = db.Column(db.Float, nullable=False)
    progress = db.Column(db.Float, default=0.0)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'target': self.target,
            'progress': self.progress,
            'completed': self.completed
        }

class Challenge(db.Model):
    __tablename__ = 'ecopulse_challenges'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    points_reward = db.Column(db.Integer, nullable=False)

class Achievement(db.Model):
    __tablename__ = 'ecopulse_achievements'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('ecopulse_users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    badge_icon = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'badge_icon': self.badge_icon,
            'created_at': self.created_at.isoformat()
        }
