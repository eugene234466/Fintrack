import sqlite3
from datetime import datetime, timedelta
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "finance.db")

def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Intialize the database with required tables"""
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date DATE NOT NULL,
            note TEXT
        )                                  
    ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT UNIQUE NOT NULL,
            monthly_limit REAL NOT NULL
        )                                  
        ''')
        conn.commit()
        

def add_transactions(type, amount, category, date, note):
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO transactions(type, amount, category, date, note) VALUES(?,?,?,?,?)",
            (type, amount, category, date, note)
        )
        conn.commit()
        
        
def get_transactions(period="weekly"):
    today = datetime.now().date()
    print(today)        
    
    if period == "weekly":
        date_filter = today - timedelta(days = 7)
        print(f"Fetching weekly transaction since {date_filter}")
    else:
        date_filter = (today - timedelta(days=180)).replace(day=1) 
        print(f"Fetching transaction data since {date_filter}")
        
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
          SELECT * FROM transactions
          WHERE date >= ?
          ORDER BY date DESC                            
        """,(date_filter,))
        
        
        transactions = cursor.fetchall() 
    return transactions

def delete_transaction(id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM transactions WHERE id = ?",
            (id,)  
        )
        conn.commit()
            
def set_budget(category, monthly_limit):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO budgets(category, monthly_limit) VALUES(?, ?)",
            (category, monthly_limit)
        )
        conn.commit()
        
        
def get_budget():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM budgets"
        )
        budgets = cursor.fetchall()
        return budgets
    
