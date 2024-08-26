import sqlite3
import os
import csv
# Function to execute the SQL file
def execute_sql_script(conn, sql_file_path):
    with open(sql_file_path, 'r') as file:
        sql_script = file.read()
    conn.executescript(sql_script)

# Function to load CSV data into a table
def load_csv_to_table(conn, csv_file_path, table_name):
    with open(csv_file_path, 'r') as file:
        reader = csv.DictReader(file)
        columns = reader.fieldnames
        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['?' for _ in columns])})"
        data = [tuple(row[col] for col in columns) for row in reader]
    
    conn.executemany(query, data)
    conn.commit()
# Create and initialize the SQLite database
def init_database():
    base_path = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current file
    database_path = os.path.join(base_path, 'wm_db.sqlite')
    init_sql_path = os.path.join(base_path, 'init.sql')
    
    conn = sqlite3.connect(database_path)
    execute_sql_script(conn, init_sql_path)
    load_csv_to_table(conn, os.path.join(base_path, 'regions.csv'), 'REGIONS')
    conn.close()

if __name__ == "__main__":
    init_database()
# command to enter db
# sqlite3 db/wm_db.sqlite