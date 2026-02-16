import sqlite3
import pandas as pd
import io

def create_usertable():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # Create user table
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT, password TEXT)')
    # Create data storage table (Stores user data as CSV strings)
    c.execute('CREATE TABLE IF NOT EXISTS user_data_storage(username TEXT, csv_content TEXT, filename TEXT)')
    conn.commit()
    conn.close()

def add_userdata(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT INTO userstable(username, password) VALUES (?,?)', (username, password))
    conn.commit()
    conn.close()
    return True

def login_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM userstable WHERE username =? AND password =?', (username, password))
    data = c.fetchall()
    conn.close()
    return data

def check_user_exists(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM userstable WHERE username =?', (username,))
    data = c.fetchall()
    conn.close()
    return data

# --- NEW FUNCTIONS FOR PERSISTENCE ---

def save_user_data(username, df, filename):
    """Saves the dataframe as a CSV string in the database."""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Convert DataFrame to CSV string
    csv_str = df.to_csv(index=False)
    
    # Delete old data for this user if it exists
    c.execute('DELETE FROM user_data_storage WHERE username = ?', (username,))
    
    # Insert new data
    c.execute('INSERT INTO user_data_storage(username, csv_content, filename) VALUES (?,?,?)', 
              (username, csv_str, filename))
    
    conn.commit()
    conn.close()

def get_user_data(username):
    """Retrieves the saved CSV string and converts it back to a DataFrame."""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT csv_content, filename FROM user_data_storage WHERE username = ?', (username,))
    result = c.fetchone()
    conn.close()
    
    if result:
        csv_str, filename = result
        # Convert CSV string back to DataFrame
        df = pd.read_csv(io.StringIO(csv_str))
        # Important: Restore date columns
        for col in ["EXPECTED DELIVERY DATE", "ACTUAL DELIVERY DATE"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])
        return df, filename
    
    return None, None
