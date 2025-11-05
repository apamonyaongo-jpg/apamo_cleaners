from flask import Flask, render_template, request, redirect, session
import sqlite3, smtplib
from config import *

app = Flask(__name__)
app.secret_key = 'apamo_secret_key'

# Initialize database
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, email TEXT, service TEXT, details TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, review TEXT)''')
    conn.commit()
    conn.close()

# Home page
@app.route('/')
def home():
    conn = sqlite3.connect('database.db')
    reviews = conn.execute('SELECT name, review FROM reviews').fetchall()
    conn.close()
    return render_template('index.html', reviews=reviews)

# Booking submission
@app.route('/book', methods=['POST'])
def book():
    name = request.form['name']
    email = request.form['email']
    service = request.form['service']
    details = request.form['details']
    conn = sqlite3.connect('database.db')
    conn.execute('INSERT INTO bookings (name, email, service, details) VALUES (?, ?, ?, ?)',
                 (name, email, service, details))
    conn.commit()
    conn.close()
    send_email(name, email, service, details)
    return redirect('/')

# Review submission
@app.route('/review', methods=['POST'])
def review():
    name = request.form['name']
    review = request.form['review']
    conn = sqlite3.connect('database.db')
    conn.execute('INSERT INTO reviews (name, review) VALUES (?, ?)', (name, review))
    conn.commit()
    conn.close()
    return redirect('/')

# Admin login
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USERNAME and request.form['password'] == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect('/dashboard')
    return render_template('login.html')

# Admin dashboard
@app.route('/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect('/admin')
    conn = sqlite3.connect('database.db')
    bookings = conn.execute('SELECT * FROM bookings').fetchall()
    reviews = conn.execute('SELECT * FROM reviews').fetchall()
    conn.close()
    return render_template('admin.html', bookings=bookings, reviews=reviews)

# Email notification
def send_email(name, email, service, details):
    message = f"""New Booking Received:
Name: {name}
Email: {email}
Service: {service}
Details: {details}
"""
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, message)
        server.quit()
    except Exception as e:
        print("Email failed:", e)

# Run the app
if __name__ == '__main__':
    init_db()
    app.run()
