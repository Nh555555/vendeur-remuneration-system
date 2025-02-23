from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from PIL import Image
import os
import cv2
import pytesseract
import numpy as np
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecretkey'

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def init_db():
    """Crée la base de données et la table sales si elles n'existent pas."""
    try:
        with sqlite3.connect('sales.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product TEXT,
                    total REAL,
                    commission REAL,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
        print("✅ Base de données 'sales.db' et table 'sales' créées avec succès.")
    except Exception as e:
        print(f"⚠️ Erreur lors de la création de la base : {e}")

users = {'admin': generate_password_hash('password123')}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and check_password_hash(users[username], password):
            # ✅ Bloc indenté correctement sous le if
            session['user'] = username
            return redirect(url_for('admin_dashboard'))
        else:
            return "Échec de la connexion"
    return render_template('login.html')


@app.route('/admin')
def admin_dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    try:
        with sqlite3.connect('sales.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM sales')
            sales = cursor.fetchall()
        return render_template('dashboard.html', sales=sales)
    except sqlite3.OperationalError as e:
        return f"❌ Erreur : {e}. La base ou la table 'sales' est manquante."

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    init_db()  # ✅ Crée la base de données avant le démarrage
    app.run(host='0.0.0.0', port=8080, debug=True, threaded=True)
