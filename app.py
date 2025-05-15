from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_pymongo import PyMongo
from flask_mail import Mail, Message
from bson.objectid import ObjectId
import random
import string
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# MongoDB Config
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo = PyMongo(app)

# Flask Mail Config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
mail = Mail(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = mongo.db.users.find_one({'email': email})
        if user:
            flash('Email already exists')
            return redirect('/register')
        otp = ''.join(random.choices(string.digits, k=6))
        session['temp_user'] = {'email': email, 'password': password, 'otp': otp}
        msg = Message('OTP Verification', sender='dpijai@gmail.com', recipients=[email])
        msg.body = f"Your OTP is: {otp}"
        mail.send(msg)
        return redirect('/verify')
    return render_template('register.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        entered_otp = request.form['otp']
        if session['temp_user']['otp'] == entered_otp:
            mongo.db.users.insert_one({
                'email': session['temp_user']['email'],
                'password': session['temp_user']['password'],
                'enrolled': []
            })
            session.pop('temp_user', None)
            flash('Registered successfully')
            return redirect('/login')
        flash('Invalid OTP')
    return render_template('verify.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = mongo.db.users.find_one({'email': email, 'password': password})
        if user:
            session['user'] = str(user['_id'])
            return redirect('/dashboard')
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    user = mongo.db.users.find_one({'_id': ObjectId(session['user'])})
    enrolled_ids = user.get('enrolled', [])
    enrolled_courses = list(mongo.db.courses.find({'_id': {'$in': [ObjectId(cid) for cid in enrolled_ids]}}))
    upcoming_courses = list(mongo.db.courses.find({'_id': {'$nin': [ObjectId(cid) for cid in enrolled_ids]}}))
    return render_template('dashboard.html', user=user, enrolled_courses=enrolled_courses, upcoming_courses=upcoming_courses)

@app.route('/enroll/<course_id>', methods=['GET', 'POST'])
def enroll(course_id):
    if 'user' not in session:
        return redirect('/login')
    if request.method == 'POST':
        mongo.db.users.update_one({"_id": ObjectId(session['user'])}, {"$addToSet": {"enrolled": course_id}})
        return redirect(f'/course/{course_id}')
    course = mongo.db.courses.find_one({'_id': ObjectId(course_id)})
    return render_template('enroll.html', course=course)

@app.route('/course/<course_id>')
def course(course_id):
    if 'user' not in session:
        return redirect('/login')
    user = mongo.db.users.find_one({'_id': ObjectId(session['user'])})
    if course_id not in user.get('enrolled', []):
        return redirect(f'/enroll/{course_id}')
    course = mongo.db.courses.find_one({'_id': ObjectId(course_id)})
    return render_template('course.html', course=course)
@app.route('/seed')
@app.route('/seed')
def seed():
    courses = [
        {
            'title': 'Java Tutorial',
            'description': 'Learn Java Basics',
            'thumbnail': 'https://drive.google.com/uc?export=view&id=1r4GGuScQ3Fk5umaLcCKzGwBE8CO4OqqY',
            'videos': [
                'https://www.youtube.com/embed/Gex-j7GlCHc',
                'https://www.youtube.com/embed/DW8QKNvWd0s',
                'https://www.youtube.com/embed/kGxSyqKbzsc',
                'https://www.youtube.com/embed/gJrjgg1KVL4'
            ],
            'pdfs': ['https://www.cs.cmu.edu/afs/cs.cmu.edu/user/gchen/www/download/java/LearnJava.pdf']
        },
        {
            'title': 'Full Stack - Introduction',
            'description': 'Intro to Full Stack Development',
            'thumbnail': 'fullstack_thumb.jpg',
            'videos': [
                'https://www.youtube.com/embed/nu_pCVPKzTk',
                'https://www.youtube.com/embed/R6RX2Zx96fE',
                'https://www.youtube.com/embed/MDZC8VDZnV8',
                'https://www.youtube.com/embed/dPMk6_HTBq8'
            ],
            'pdfs': ['https://ucbxwebsite.z13.web.core.windows.net/docs/FullStackWebDev_CourseReader_FirstChapter.pdf']
        },
        {
            'title': 'ARTIFICIAL INTELLIGENCE - Introduction',
            'description': 'This course contains a brief about AI, Machine Learning and Neural networks',
            'thumbnail': 'fullstack_thumb.jpg',
            'videos': [
                'https://www.youtube.com/embed/ts0mU1_fQVA',
                'https://www.youtube.com/embed/HFTvaOjWk2c',
                'https://www.youtube.com/embed/HFTvaOjWk2c',
                'https://www.youtube.com/embed/HFTvaOjWk2c'
            ],
            'pdfs': ['https://drive.google.com/file/d/another_file_id/view']
        },
        {
            'title': 'Internet of Things - Introduction',
            'description': 'This courses is intende for CSE/ECE undergrads for embedded systems.',
            'thumbnail': 'fullstack_thumb.jpg',
            'videos': [
                'https://www.youtube.com/embed/ts0mU1_fQVA',
                'https://www.youtube.com/embed/HFTvaOjWk2c',
                'https://www.youtube.com/embed/HFTvaOjWk2c',
                'https://www.youtube.com/embed/HFTvaOjWk2c'
            ],
            'pdfs': ['https://drive.google.com/file/d/another_file_id/view']
        },
        {
            'title': 'Operating system Fundamentals',
            'description': 'This course id designed for basic OS concepts scheduling, RTOS and working in linux environment',
            'thumbnail': 'fullstack_thumb.jpg',
            'videos': [
                'https://www.youtube.com/embed/ts0mU1_fQVA',
                'https://www.youtube.com/embed/HFTvaOjWk2c',
                'https://www.youtube.com/embed/HFTvaOjWk2c',
                'https://www.youtube.com/embed/HFTvaOjWk2c'
            ],
            'pdfs': ['https://drive.google.com/file/d/another_file_id/view']
        }


    ]

    for course in courses:
        existing = mongo.db.courses.find_one({'title': course['title']})
        if not existing:
            mongo.db.courses.insert_one(course)

    return 'Courses seeded (skipping duplicates)'



if __name__ == '__main__':
    app.run(debug=True)


#end of code