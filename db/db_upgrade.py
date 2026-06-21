import sqlite3
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'godseye.db'))

def upgrade():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if we already upgraded
    cursor.execute("PRAGMA table_info(Theses)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if "is_tracked" not in columns:
        print("Upgrading Theses table...")
        cursor.execute("ALTER TABLE Theses ADD COLUMN is_tracked BOOLEAN DEFAULT 0")
        cursor.execute("ALTER TABLE Theses ADD COLUMN is_starred BOOLEAN DEFAULT 0")
        cursor.execute("ALTER TABLE Theses ADD COLUMN alpha_score FLOAT DEFAULT 0")
        cursor.execute("ALTER TABLE Theses ADD COLUMN trend VARCHAR DEFAULT 'NEUTRAL'")
        cursor.execute("ALTER TABLE Theses ADD COLUMN target_instrument VARCHAR")
        cursor.execute("ALTER TABLE Theses ADD COLUMN position_type VARCHAR")
        cursor.execute("ALTER TABLE Theses ADD COLUMN entry_price FLOAT")
        cursor.execute("ALTER TABLE Theses ADD COLUMN current_price FLOAT")
        cursor.execute("ALTER TABLE Theses ADD COLUMN pnl_percentage FLOAT")

    if "title" not in columns:
        print("Upgrading Theses table with title...")
        cursor.execute("ALTER TABLE Theses ADD COLUMN title VARCHAR")
        
    cursor.execute("PRAGMA table_info(Assumptions)")
    columns = [col[1] for col in cursor.fetchall()]
    if "status" not in columns:
        print("Upgrading Assumptions table...")
        cursor.execute("ALTER TABLE Assumptions ADD COLUMN status VARCHAR DEFAULT 'NEUTRAL'")
        
    conn.commit()
    conn.close()
    print("Database upgrade complete.")

if __name__ == "__main__":
    upgrade()
