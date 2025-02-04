from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'youtuber' or 'editor'
    is_verified = db.Column(db.Boolean, default=False)  # Email verification status
    verification_token = db.Column(db.String(100), unique=True)  # Verification token

    # OAuth Tokens for YouTube API Integration
    access_token = db.Column(db.String(500), nullable=True)
    refresh_token = db.Column(db.String(500), nullable=True)
    token_expiry = db.Column(db.DateTime, nullable=True)

    # YouTube Channel Info (for YouTubers)
    youtube_channel_id = db.Column(db.String(100), unique=True, nullable=True)

    # Account Tracking
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # Account creation time
    last_login = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())  # Last login timestamp
