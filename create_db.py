import sqlite3
import os

def create_database():
    db_path = os.path.abspath('sales.db')
    print(f"📂 Chemin de la base : {db_path}")
    try:
        conn = sqlite3.connect(db_path)
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
        conn.close()
        print("✅ Base de données 'sales.db' et table 'sales' créées avec succès.")
    except Exception as e:
        print(f"❌ Erreur : {e}")

if __name__ == "__main__":
    create_database()
