from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_pymongo import PyMongo
from flask_mail import Mail, Message
from bson.objectid import ObjectId
import random
import string

app = Flask(__name__)
app.secret_key = 'secret123'

# MongoDB Config
app.config["MONGO_URI"] = "mongodb+srv://jaiwantdact2023:jaiwantD576@cluster0.daleap2.mongodb.net/e_learning?retryWrites=true&w=majority&appName=Cluster0"
mongo = PyMongo(app)

# Flask Mail Config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'dpijai@gmail.com'
app.config['MAIL_PASSWORD'] = 'rmtq ieqg eylk ovsb'
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
    courses = mongo.db.courses.find()
    return render_template('dashboard.html', user=user, courses=courses)

@app.route('/enroll/<course_id>')
def enroll(course_id):
    if 'user' not in session:
        return redirect('/login')
    mongo.db.users.update_one({"_id": ObjectId(session['user'])}, {"$addToSet": {"enrolled": course_id}})
    return redirect(f'/course/{course_id}')

@app.route('/course/<course_id>')
def course(course_id):
    if 'user' not in session:
        return redirect('/login')
    user = mongo.db.users.find_one({'_id': ObjectId(session['user'])})
    if course_id not in user.get('enrolled', []):
        return redirect('/dashboard')
    course = mongo.db.courses.find_one({'_id': ObjectId(course_id)})
    return render_template('course.html', course=course)

# One-time course seeding route
@app.route('/seed')
def seed():
    mongo.db.courses.insert_many([
        {'title': 'Java Tutorial', 'description': 'Learn Java Basics', 'videos': ['java_intro.mp4'], 'pdfs': ['java_notes.pdf']},
        {'title': 'Full Stack - Introduction', 'description': 'Intro to Full Stack Development', 'videos': ['fullstack_intro.mp4'], 'pdfs': ['fullstack_notes.pdf']}
    ])
    return 'Courses seeded'

if __name__ == '__main__':
    app.run(debug=True)
