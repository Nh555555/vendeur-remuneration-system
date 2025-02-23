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

# 📂 CHEMIN DE BASE DYNAMIQUE
DB_PATH = '/data/sales.db'
DATA_FOLDER = '/data'

def init_db():
    try:
        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)
            print(f"📁 Dossier {DATA_FOLDER} créé avec succès.")
        if not os.path.exists(DB_PATH):
            print(f"📂 Création de la base : {DB_PATH}")
        with sqlite3.connect(DB_PATH) as conn:
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
        print(f"✅ Base et tables créées dans {DB_PATH}.")
    except Exception as e:
        print(f"❌ Erreur création base : {e}")

def create_default_seller():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(\"SELECT * FROM sellers WHERE username=?\", ('vendeur',))
        if not cursor.fetchone():
            cursor.execute(\"INSERT INTO sellers (username, password) VALUES (?, ?)\",
                           ('vendeur', generate_password_hash('vendeur123')))\n            conn.commit()\n        print(\"✅ Vendeur par défaut créé.\")\n\n@app.route('/')\ndef home():\n    return render_template('index.html')\n\n@app.route('/login', methods=['GET', 'POST'])\ndef login():\n    if request.method == 'POST':\n        username = request.form['username']\n        password = request.form['password']\n        with sqlite3.connect(DB_PATH) as conn:\n            cursor = conn.cursor()\n            cursor.execute(\"SELECT password FROM sellers WHERE username=?\", (username,))\n            seller = cursor.fetchone()\n            if seller and check_password_hash(seller[0], password):\n                session['seller'] = username\n                return redirect(url_for('seller_dashboard'))\n        return \"Échec de la connexion\"\n    return render_template('login.html')\n\n@app.route('/seller')\ndef seller_dashboard():\n    if 'seller' not in session:\n        return redirect(url_for('login'))\n    with sqlite3.connect(DB_PATH) as conn:\n        cursor = conn.cursor()\n        cursor.execute('SELECT * FROM sales WHERE seller=?', (session['seller'],))\n        sales = cursor.fetchall()\n    return render_template('seller_dashboard.html', sales=sales, seller=session['seller'])\n\n@app.route('/logout')\ndef logout():\n    session.pop('seller', None)\n    return redirect(url_for('home'))\n\nif __name__ == '__main__':\n    print(\"🚀 Lancement de l'application avec gestion avancée du dossier /data...\")\n    init_db()\n    create_default_seller()\n    print(\"🟢 Serveur opérationnel.\")\n    app.run(host='0.0.0.0', port=8080, debug=True, threaded=True)"}]}
