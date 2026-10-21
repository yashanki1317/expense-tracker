from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import re
from dotenv import load_dotenv
from functools import wraps
from datetime import datetime

load_dotenv() # Load environment variables from .env file

app = Flask(__name__)
app.secret_key = 'cost_spending_tracker_secret_key_v1' # Secure secret key

# Database Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'cost_v2.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    reminders = db.relationship('Reminder', backref='user', lazy=True)
    categories = db.relationship('Category', backref='user', lazy=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'income' or 'expense'
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    payment_mode = db.Column(db.String(10), nullable=False) # 'cash' or 'online'
    description = db.Column(db.String(200), nullable=True)
    date = db.Column(db.String(20), nullable=False)
    last_modified = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=True)
    due_date = db.Column(db.String(20), nullable=False)
    type = db.Column(db.String(20), nullable=False) # 'bill' or 'receivable'

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    __table_args__ = (db.UniqueConstraint('user_id', 'name', name='_user_category_uc'),)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Unauthorized'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    if len(str(password)) < 4:
        return jsonify({'error': 'Password must be at least 4 digits'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    # Add default categories for new user
    default_categories = ['Food', 'Rent', 'Transport', 'Salary', 'Shopping', 'Other']
    for cat_name in default_categories:
        db.session.add(Category(name=cat_name, user_id=new_user.id))
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        session['username'] = user.username
        return jsonify({'message': 'Logged in successfully'})
    
    return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# API for Transactions
@app.route('/api/transactions', methods=['GET'])
@login_required
def get_transactions():
    transactions = Transaction.query.filter_by(user_id=session['user_id']).all()
    return jsonify([{
        'id': t.id, 'type': t.type, 'amount': t.amount, 'category': t.category,
        'payment_mode': t.payment_mode, 'description': t.description, 'date': t.date,
        'last_modified': t.last_modified.isoformat() if t.last_modified else None
    } for t in transactions])

@app.route('/api/transactions', methods=['POST'])
@login_required
def add_transaction():
    data = request.get_json()
    new_t = Transaction(
        user_id=session['user_id'],
        type=data['type'],
        amount=data['amount'],
        category=data['category'],
        payment_mode=data['payment_mode'],
        description=data.get('description', ''),
        date=data['date']
    )
    db.session.add(new_t)
    db.session.commit()
    return jsonify({'id': new_t.id}), 201

@app.route('/api/transactions/<int:id>', methods=['PUT'])
@login_required
def update_transaction(id):
    t = Transaction.query.filter_by(id=id, user_id=session['user_id']).first_or_404()
    data = request.get_json()
    t.type = data['type']
    t.amount = data['amount']
    t.category = data['category']
    t.payment_mode = data['payment_mode']
    t.description = data.get('description', '')
    t.date = data['date']
    db.session.commit()
    return jsonify({'message': 'Updated'})

@app.route('/api/transactions/<int:id>', methods=['DELETE'])
@login_required
def delete_transaction(id):
    t = Transaction.query.filter_by(id=id, user_id=session['user_id']).first_or_404()
    db.session.delete(t)
    db.session.commit()
    return jsonify({'message': 'Deleted'})

# API for Reminders
@app.route('/api/reminders', methods=['GET'])
@login_required
def get_reminders():
    reminders = Reminder.query.filter_by(user_id=session['user_id']).all()
    return jsonify([{
        'id': r.id, 'title': r.title, 'amount': r.amount, 'due_date': r.due_date, 'type': r.type
    } for r in reminders])

@app.route('/api/reminders', methods=['POST'])
@login_required
def add_reminder():
    data = request.get_json()
    new_reminder = Reminder(
        user_id=session['user_id'],
        title=data['title'],
        amount=data.get('amount'),
        due_date=data['due_date'],
        type=data['type']
    )
    db.session.add(new_reminder)
    db.session.commit()
    return jsonify({'id': new_reminder.id}), 201

@app.route('/api/reminders/<int:id>', methods=['DELETE'])
@login_required
def delete_reminder(id):
    r = Reminder.query.filter_by(id=id, user_id=session['user_id']).first_or_404()
    db.session.delete(r)
    db.session.commit()
    return jsonify({'message': 'Deleted'})

# API for Categories
@app.route('/api/categories', methods=['GET'])
@login_required
def get_categories():
    user_id = session['user_id']
    
    # Ensure 'Transfer' category exists for the user (non-removable logic)
    if not Category.query.filter_by(user_id=user_id, name='Transfer').first():
        db.session.add(Category(user_id=user_id, name='Transfer'))
        db.session.commit()
        
    categories = Category.query.filter_by(user_id=user_id).all()
    return jsonify([c.name for c in categories])

@app.route('/api/categories', methods=['POST'])
@login_required
def add_category():
    data = request.get_json()
    new_name = data.get('name', '').strip()
    
    # Restriction: User cannot create a category named 'Transfer'
    if new_name.lower() == 'transfer':
        return jsonify({'error': 'Category "Transfer" is reserved for system use.'}), 400
        
    if Category.query.filter_by(user_id=session['user_id'], name=new_name).first():
        return jsonify({'error': 'Category exists'}), 400
    
    new_cat = Category(user_id=session['user_id'], name=new_name)
    db.session.add(new_cat)
    db.session.commit()
    return jsonify({'message': 'Created'}), 201

@app.route('/api/categories/<name>', methods=['DELETE'])
@login_required
def delete_category(name):
    cat = Category.query.filter_by(user_id=session['user_id'], name=name).first_or_404()
    db.session.delete(cat)
    db.session.commit()
    return jsonify({'message': 'Deleted'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Simplified startup for sandbox stability
    print("Starting Flask App on port 5001...")
    app.run(port=5001, debug=False, use_reloader=False)
