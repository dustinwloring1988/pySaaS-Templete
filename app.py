# app.py

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from twilio.rest import Client
import os
import requests
import random
from dotenv import load_dotenv
from datetime import datetime, timedelta
import jwt

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Twilio and Mailgun configuration
twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')
twilio_client = Client(twilio_account_sid, twilio_auth_token)

mailgun_api_key = os.getenv('MAILGUN_API_KEY')
mailgun_domain = os.getenv('MAILGUN_DOMAIN')

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        phone_number = request.form['phone_number']

        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists.')
            return redirect(url_for('register'))

        new_user = User(username=username, email=email, phone_number=phone_number)
        new_user.password_hash = generate_password_hash(password)

        db.session.add(new_user)
        db.session.commit()

        # Send verification code via Twilio
        verification_code = str(random.randint(100000, 999999))
        twilio_client.messages.create(
            body=f"Your verification code is: {verification_code}",
            from_=twilio_phone_number,
            to=phone_number
        )

        flash('Registered successfully. Please check your phone for the verification code.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')

    return render_template('login.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()

        if user:
            # Generate password reset token
            reset_token = jwt.encode({
                'user_id': user.id,
                'exp': datetime.utcnow() + timedelta(hours=1)
            }, app.config['SECRET_KEY'], algorithm='HS256')

            reset_link = url_for('reset_password', token=reset_token, _external=True)

            # Send password reset email via Mailgun
            requests.post(
                f"https://api.mailgun.net/v3/{mailgun_domain}/messages",
                auth=("api", mailgun_api_key),
                data={
                    "from": f"Your App <mailgun@{mailgun_domain}>",
                    "to": [email],
                    "subject": "Password Reset",
                    "text": f"Click the following link to reset your password: {reset_link}"
                }
            )

            flash('Password reset link sent to your email.')
            return redirect(url_for('login'))
        else:
            flash('Email not found.')

    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        token_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = token_data['user_id']
        user = User.query.get(user_id)

        if request.method == 'POST':
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']

            if new_password == confirm_password:
                user.password_hash = generate_password_hash(new_password)
                db.session.commit()
                flash('Your password has been reset successfully.')
                return redirect(url_for('login'))
            else:
                flash('Passwords do not match.')

        return render_template('reset_password.html', token=token)
    except jwt.ExpiredSignatureError:
        flash('The password reset link has expired.')
        return redirect(url_for('forgot_password'))
    except jwt.InvalidTokenError:
        flash('Invalid reset link.')
        return redirect(url_for('forgot_password'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.username = request.form['username']
        current_user.email = request.form['email']
        current_user.phone_number = request.form['phone_number']
        
        if request.form['new_password']:
            if request.form['new_password'] == request.form['confirm_password']:
                current_user.password_hash = generate_password_hash(request.form['new_password'])
            else:
                flash('Passwords do not match', 'danger')
                return redirect(url_for('edit_profile'))
        
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('edit_profile.html')

@app.route('/cancel-account', methods=['GET', 'POST'])
@login_required
def cancel_account():
    if request.method == 'POST':
        if request.form['confirm'] == 'CANCEL':
            db.session.delete(current_user)
            db.session.commit()
            logout_user()
            flash('Your account has been cancelled', 'success')
            return redirect(url_for('index'))
        else:
            flash('Please type CANCEL to confirm account cancellation', 'danger')
    
    return render_template('cancel_account.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
