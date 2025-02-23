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
    try:
        db_path = '/data/sales.db'
        if not os.path.exists('/data'):
            os.makedirs('/data')
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product TEXT,
                    total REAL,
                    commission REAL,
                    seller TEXT,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sellers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT
                )
            ''')
            conn.commit()
    except Exception as e:
        print(f"❌ Erreur lors de la création de la base : {e}")

def create_default_seller():
    db_path = '/data/sales.db'
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sellers WHERE username=?", ('vendeur',))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO sellers (username, password) VALUES (?, ?)",
                           ('vendeur', generate_password_hash('vendeur123')))
            conn.commit()
        print("✅ Vendeur par défaut créé.")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db_path = '/data/sales.db'
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM sellers WHERE username=?", (username,))
            seller = cursor.fetchone()
            if seller and check_password_hash(seller[0], password):
                session['seller'] = username
                return redirect(url_for('seller_dashboard'))
        return "Échec de la connexion"
    return render_template('login.html')

@app.route('/seller')
def seller_dashboard():
    if 'seller' not in session:
        return redirect(url_for('login'))
    db_path = '/data/sales.db'
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM sales WHERE seller=?', (session['seller'],))
        sales = cursor.fetchall()
    return render_template('seller_dashboard.html', sales=sales, seller=session['seller'])

@app.route('/add_sale', methods=['GET', 'POST'])
def add_sale():
    if 'seller' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        product = request.form['product']
        total = float(request.form['total'])
        commission = total * 0.05
        db_path = '/data/sales.db'
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO sales (product, total, commission, seller) VALUES (?, ?, ?, ?)',
                           (product, total, commission, session['seller']))
            conn.commit()
        return redirect(url_for('seller_dashboard'))
    return render_template('add_sale.html')

@app.route('/logout')
def logout():
    session.pop('seller', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    print("🚀 Lancement de l'application...")
    init_db()
    create_default_seller()
    print("🟢 Serveur en cours d'exécution.")
    app.run(host='0.0.0.0', port=8080, debug=True, threaded=True)
