"""
Student Management System - Backend REST API
Framework : Flask
Database  : PostgreSQL / MySQL / SQLite (dev default)
Auth      : JWT (flask-jwt-extended)

Run:
    pip install -r requirements.txt
    python app.py
"""

import os
from datetime import timedelta, datetime

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required,
    get_jwt_identity, get_jwt
)
from werkzeug.security import generate_password_hash, check_password_hash

# ----------------------------------------------------------------------
# App Config
# ----------------------------------------------------------------------
app = Flask(__name__)
CORS(app)  # frontend origin থেকে request allow করার জন্য

# ---- Database URL ----
# SQLite দিয়ে দ্রুত টেস্ট করা যাবে (ডিফল্ট)। প্রোডাকশনে MySQL/PostgreSQL ব্যবহার করুন:
#
# PostgreSQL: postgresql://username:password@localhost:5432/student_db
# MySQL     : mysql+pymysql://username:password@localhost:3306/student_db
#
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'sqlite:///student_management.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ---- JWT Config ----
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'change-this-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=6)

db = SQLAlchemy(app)
jwt = JWTManager(app)


# ----------------------------------------------------------------------
# Models
# ----------------------------------------------------------------------
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='admin')  # admin / teacher
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role
        }


class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    roll = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    department = db.Column(db.String(100))
    semester = db.Column(db.String(20))
    address = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'roll': self.roll,
            'email': self.email,
            'phone': self.phone,
            'department': self.department,
            'semester': self.semester,
            'address': self.address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ----------------------------------------------------------------------
# Auth Routes
# ----------------------------------------------------------------------
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'admin')

    if not username or not email or not password:
        return jsonify({'message': 'username, email, password দরকার'}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({'message': 'এই username অথবা email দিয়ে আগেই একাউন্ট আছে'}), 409

    user = User(username=username, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'রেজিস্ট্রেশন সফল হয়েছে', 'user': user.to_dict()}), 201


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({'message': 'ভুল username বা password'}), 401

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={'role': user.role, 'username': user.username}
    )
    return jsonify({
        'message': 'লগইন সফল হয়েছে',
        'access_token': access_token,
        'user': user.to_dict()
    }), 200


@app.route('/api/me', methods=['GET'])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'ইউজার পাওয়া যায়নি'}), 404
    return jsonify(user.to_dict()), 200


# ----------------------------------------------------------------------
# Student CRUD Routes  (সব রুট JWT প্রোটেক্টেড)
# ----------------------------------------------------------------------
@app.route('/api/students', methods=['GET'])
@jwt_required()
def get_students():
    # ?q=  দিয়ে name/roll/department সার্চ করা যাবে
    query = Student.query
    search = request.args.get('q')
    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(Student.name.ilike(like),
                   Student.roll.ilike(like),
                   Student.department.ilike(like))
        )

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    pagination = query.order_by(Student.id.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'students': [s.to_dict() for s in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages
    }), 200


@app.route('/api/students/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'message': 'স্টুডেন্ট পাওয়া যায়নি'}), 404
    return jsonify(student.to_dict()), 200


@app.route('/api/students', methods=['POST'])
@jwt_required()
def create_student():
    data = request.get_json() or {}
    name = data.get('name')
    roll = data.get('roll')

    if not name or not roll:
        return jsonify({'message': 'name এবং roll আবশ্যক'}), 400

    if Student.query.filter_by(roll=roll).first():
        return jsonify({'message': 'এই roll নাম্বার দিয়ে আগেই স্টুডেন্ট আছে'}), 409

    student = Student(
        name=name,
        roll=roll,
        email=data.get('email'),
        phone=data.get('phone'),
        department=data.get('department'),
        semester=data.get('semester'),
        address=data.get('address'),
    )
    db.session.add(student)
    db.session.commit()

    return jsonify({'message': 'স্টুডেন্ট সফলভাবে যোগ হয়েছে', 'student': student.to_dict()}), 201


@app.route('/api/students/<int:student_id>', methods=['PUT'])
@jwt_required()
def update_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'message': 'স্টুডেন্ট পাওয়া যায়নি'}), 404

    data = request.get_json() or {}
    for field in ['name', 'roll', 'email', 'phone', 'department', 'semester', 'address']:
        if field in data:
            setattr(student, field, data[field])

    db.session.commit()
    return jsonify({'message': 'স্টুডেন্ট আপডেট হয়েছে', 'student': student.to_dict()}), 200


@app.route('/api/students/<int:student_id>', methods=['DELETE'])
@jwt_required()
def delete_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'message': 'স্টুডেন্ট পাওয়া যায়নি'}), 404

    db.session.delete(student)
    db.session.commit()
    return jsonify({'message': 'স্টুডেন্ট ডিলিট হয়েছে'}), 200


# ----------------------------------------------------------------------
# Dashboard Stats (optional, extra endpoint)
# ----------------------------------------------------------------------
@app.route('/api/stats', methods=['GET'])
@jwt_required()
def stats():
    total_students = Student.query.count()
    dept_counts = db.session.query(
        Student.department, db.func.count(Student.id)
    ).group_by(Student.department).all()

    return jsonify({
        'total_students': total_students,
        'by_department': [{'department': d or 'N/A', 'count': c} for d, c in dept_counts]
    }), 200


# ----------------------------------------------------------------------
# JWT Error Handlers (ভালো error message দেয়ার জন্য)
# ----------------------------------------------------------------------
@jwt.unauthorized_loader
def unauthorized_response(callback):
    return jsonify({'message': 'Token পাওয়া যায়নি, দয়া করে লগইন করুন'}), 401


@jwt.expired_token_loader
def expired_token_response(jwt_header, jwt_payload):
    return jsonify({'message': 'Token এর মেয়াদ শেষ, আবার লগইন করুন'}), 401


@jwt.invalid_token_loader
def invalid_token_response(callback):
    return jsonify({'message': 'ভুল Token'}), 401


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # প্রথমবার রান করলে টেবিল তৈরি হবে

        # ডিফল্ট admin একাউন্ট (না থাকলে) — শুধু ডেভেলপমেন্টের সুবিধার জন্য
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', email='admin@example.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print(">> ডিফল্ট admin একাউন্ট তৈরি হয়েছে -> username: admin | password: admin123")

    app.run(debug=True, port=5000)
