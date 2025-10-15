import sqlite3

def get_db():
    conn = sqlite3.connect('helpdesk.db')
    conn.row_factory = sqlite3.Row
    return conn

def setup_database():
    db = get_db()
    
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    db.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT DEFAULT 'Open',
            user_id INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create default admin user
    import auth
    admin_password = auth.hash_password("admin123")
    db.execute("INSERT OR IGNORE INTO users (email, password, full_name, role) VALUES (?, ?, ?, ?)",
              ("admin@helpdesk.com", admin_password, "System Admin", "admin"))
    
    db.commit()
    db.close()
    print("✅ Database is ready!")

setup_database()