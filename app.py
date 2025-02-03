from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from flask_migrate import Migrate
import secrets

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-123'  # Replace with a real secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Replace with your email provider
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'your-email-password'  # Replace with your email password
mail = Mail(app)

# Initialize SQLAlchemy for database management
db = SQLAlchemy(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Initialize Flask-Login for session management
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- Define Database Models ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(20))  # 'youtuber' or 'editor'
    is_verified = db.Column(db.Boolean, default=False)  # Email verification status
    verification_token = db.Column(db.String(100), unique=True)  # Verification token

# --- Load Users for Flask-Login ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Routes ---
@app.route('/')
def home():
    return "Welcome to SafeEdit! <a href='/login'>Login</a> or <a href='/register'>Register</a>"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        # Check if user already exists
        user = User.query.filter_by(email=email).first()
        if user:
            return "User already exists! <a href='/login'>Login here</a>"

        # Generate a verification token
        verification_token = secrets.token_urlsafe(32)

        # Create new user
        new_user = User(
            email=email,
            password=generate_password_hash(password),
            role=role,
            verification_token=verification_token
        )
        db.session.add(new_user)
        db.session.commit()

        # Send verification email
        send_verification_email(email, verification_token)

        return "Registration successful! Please check your email to verify your account."

    return render_template('register.html')

def send_verification_email(email, token):
    msg = Message('Verify Your Email', sender='your-email@gmail.com', recipients=[email])
    verification_link = f"http://localhost:5000/verify-email/{token}"
    msg.body = f"Click the link to verify your email: {verification_link}"
    mail.send(msg)

@app.route('/verify-email/<token>')
def verify_email(token):
    user = User.query.filter_by(verification_token=token).first()
    if user:
        user.is_verified = True
        user.verification_token = None  # Clear the token after verification
        db.session.commit()
        return "Email verified successfully! <a href='/login'>Login here</a>"
    else:
        return "Invalid or expired verification link."

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            if user.is_verified:
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                return "Please verify your email before logging in."
        else:
            return "Invalid email or password! <a href='/login'>Try again</a>"

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return f"Hello, {current_user.email}! You are a {current_user.role}."

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

# --- Run the App ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables if they don't exist
    app.run(debug=True)