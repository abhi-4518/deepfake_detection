import sqlite3
from datetime import datetime

# Connect to database
conn = sqlite3.connect('deepfaker.db')
cursor = conn.cursor()

try:
    # Check if created_at column exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'created_at' not in columns:
        print("Adding 'created_at' column to users table...")
        
        # Add column with NULL default (SQLite limitation)
        cursor.execute("ALTER TABLE users ADD COLUMN created_at TIMESTAMP")
        
        # Update existing rows with current timestamp
        cursor.execute("UPDATE users SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
        
        conn.commit()
        print("✅ Column added successfully!")
    else:
        print("✅ Column 'created_at' already exists.")
    
    # Verify the change
    cursor.execute("PRAGMA table_info(users)")
    print("\nCurrent users table schema:")
    for column in cursor.fetchall():
        print(f"  - {column[1]} ({column[2]})")
    
    # Show existing users
    cursor.execute("SELECT id, username, created_at FROM users")
    users = cursor.fetchall()
    if users:
        print(f"\n✅ Existing users ({len(users)}):")
        for user in users:
            print(f"  - ID: {user[0]}, Username: {user[1]}, Created: {user[2]}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()
finally:
    conn.close()

print("\n✅ Database migration complete! You can now restart the app.")
