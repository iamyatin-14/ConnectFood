import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session
import random
import string
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Replace with your actual secret key

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.example.com'  # Replace with your SMTP server details
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'ycreation777@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'Yzafhk789'  # Replace with your email password

mail = Mail(app)

# Function to create a connection to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('database/connectfood.db')
    conn.row_factory = sqlite3.Row
    return conn

# Function to initialize the database schema
def init_database():
    conn = get_db_connection()
    with app.open_resource('database/schema.sql', mode='r') as f:
        conn.cursor().executescript(f.read())
    conn.commit()
    conn.close()

# Initialize the database if not already initialized
init_database()

# Function to generate OTP
def generate_otp():
    digits = string.digits
    return ''.join(random.choice(digits) for i in range(6))

# Function to send OTP via email
def send_otp_email(email, otp):
    msg = Message('OTP for CONNECT-FOOD Registration',
                  sender='your_email@example.com',
                  recipients=[email])
    msg.body = f'Your OTP for registration is: {otp}'
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False

# Route for home page
@app.route('/')
def index():
    return render_template('index.html')

# Route for admin login
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    # Placeholder for admin credentials (replace with actual admin login logic)
    admin_username = 'admin'
    admin_password = 'adminpass'

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == admin_username and password == admin_password:
            flash('Admin login successful.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('admin_login.html')

# Route for admin dashboard (to view new registration requests)
@app.route('/admin_dashboard')
def admin_dashboard():
    # Placeholder for fetching new registration requests from database
    new_restaurants = []
    new_orphanages = []

    return render_template('admin_dashboard.html', new_restaurants=new_restaurants, new_orphanages=new_orphanages)

# Route for restaurant login
@app.route('/restaurant_login', methods=['GET', 'POST'])
def restaurant_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM restaurants WHERE email = ? AND password = ?', (email, password))
        user = cur.fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['user_type'] = 'restaurant'
            return redirect(url_for('restaurant'))
        else:
            flash('Login failed. Please check your email and password.', 'error')

    return render_template('restaurant_login.html')

# Route for restaurant registration
@app.route('/restaurant_register', methods=['GET', 'POST'])
def restaurant_register():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        location = request.form['location']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Generate OTP
        otp = generate_otp()

        # Send OTP via email
        if send_otp_email(email, otp):
            session['otp'] = otp  # Store OTP in session for verification
            flash('OTP sent to your email. Please enter the OTP to complete registration.', 'info')
        else:
            flash('Failed to send OTP. Please try again later.', 'error')
            return redirect(url_for('restaurant_register'))

        # Verify passwords match
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('restaurant_register'))

        # Save user data to database (placeholder)
        conn = get_db_connection()
        conn.execute('INSERT INTO restaurants (username, location, email, password) VALUES (?, ?, ?, ?)',
                     (username, location, email, password))
        conn.commit()
        conn.close()

        flash('Registration request submitted. Waiting for admin approval.', 'success')
        return redirect(url_for('restaurant_login'))

    return render_template('restaurant_register.html')

# Route for orphanage/home login
@app.route('/orphanage_login', methods=['GET', 'POST'])
def orphanage_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM orphanages WHERE email = ? AND password = ?', (email, password))
        user = cur.fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['user_type'] = 'orphanage'
            return redirect(url_for('orphanage'))
        else:
            flash('Login failed. Please check your email and password.', 'error')

    return render_template('orphanage_login.html')

# Route for orphanage/home registration
@app.route('/orphanage_register', methods=['GET', 'POST'])
def orphanage_register():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        location = request.form['location']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Generate OTP
        otp = generate_otp()

        # Send OTP via email
        if send_otp_email(email, otp):
            session['otp'] = otp  # Store OTP in session for verification
            flash('OTP sent to your email. Please enter the OTP to complete registration.', 'info')
        else:
            flash('Failed to send OTP. Please try again later.', 'error')
            return redirect(url_for('orphanage_register'))

        # Verify passwords match
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('orphanage_register'))

        # Save user data to database (placeholder)
        conn = get_db_connection()
        conn.execute('INSERT INTO orphanages (username, location, email, password) VALUES (?, ?, ?, ?)',
                     (username, location, email, password))
        conn.commit()
        conn.close()

        flash('Registration request submitted. Waiting for admin approval.', 'success')
        return redirect(url_for('orphanage_login'))

    return render_template('orphanage_register.html')

# Route for restaurant dashboard
@app.route('/restaurant')
def restaurant():
    if 'user_id' not in session or session['user_type'] != 'restaurant':
        return redirect(url_for('restaurant_login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM food_postings WHERE user_id = ?', (session['user_id'],))
    food_postings = cur.fetchall()
    conn.close()

    return render_template('restaurant_dashboard.html', food_postings=food_postings)

# Route for posting food by restaurant
@app.route('/post_food', methods=['GET', 'POST'])
def post_food():
    if request.method == 'POST':
        date = request.form['date']
        time = request.form['time']
        available_food = request.form['available_food']

        # Logic to save food posting to database (placeholder)
        # Example:
        # save_food_posting(date, time, available_food, session['user_id'])

        flash('Food posting submitted successfully.', 'success')
        return redirect(url_for('restaurant'))

    return render_template('post_food.html')

# Route for orphanage/home dashboard
@app.route('/orphanage')
def orphanage():
    if 'user_id' not in session or session['user_type'] != 'orphanage':
        return redirect(url_for('orphanage_login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM food_postings')
    food_postings = cur.fetchall()
    conn.close()

    return render_template('orphanage_dashboard.html', food_postings=food_postings)

# Route for selecting pickup by orphanage
@app.route('/select_pickup', methods=['GET', 'POST'])
def select_pickup():
    if request.method == 'POST':
        posting_id = request.form['posting_id']

        # Logic to update pickup status to "Picked up" (placeholder)
        # Example:
        # update_pickup_status(posting_id)

        flash('Pickup confirmed successfully.', 'success')
        return redirect(url_for('orphanage'))

    return render_template('select_pickup.html')

if __name__ == '__main__':
    app.run(debug=True)
