import sqlite3

def create_database():
    try:
        conn = sqlite3.connect('sales.db')
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
        print(f"❌ Erreur lors de la création de la base : {e}")

if __name__ == "__main__":
    create_database()
