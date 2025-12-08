import sqlite3
import os

def inspect_users():
    db_path = 'skinpredict.db'
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all users
        cursor.execute("SELECT id, email, role, firebase_uid FROM users")
        users = cursor.fetchall()
        
        if not users:
            print("No users found in the database.")
        else:
            print("\n=== Users in Database ===")
            print(f"{'ID':<5} | {'Email':<30} | {'Role':<15} | {'Firebase UID'}")
            print("-" * 80)
            for user in users:
                print(f"{user[0]:<5} | {user[1]:<30} | {user[2]:<15} | {user[3]}")
            
        conn.close()
        
    except Exception as e:
        print(f"Error reading database: {e}")

if __name__ == "__main__":
    inspect_users()
