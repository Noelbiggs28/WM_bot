import gspread
import os
from dotenv import load_dotenv
import sqlite3
load_dotenv()

def update_google_sheet():
    # Google Sheet initialization
    spreadsheet_ID = os.environ.get('SPREADSHEET_ID')
    gc = gspread.service_account(filename='wmac_key.json')
    sh = gc.open_by_key(spreadsheet_ID)
    activity_sheet = sh.worksheet('Activity')
    conn = sqlite3.connect('db/wm_db.sqlite')
    cursor = conn.cursor()

    # Fetch column names from the SQLite database, excluding the first column (id)
    cursor.execute("PRAGMA table_info(Tracker)")
    columns = [info[1] for info in cursor.fetchall()][1:]  # Skip the first column

    # Fetch data from the SQLite database, excluding the first column
    cursor.execute("SELECT user_role, user_name, nick_name, last_activity_date, days_inactive, maps_participated_in, maps_won, maps_lost, notes FROM Tracker")
    data = cursor.fetchall()

    # Prepare data for batch update
    rows_to_update = [columns]  # Start with the column headers
    rows_to_update.extend(data)  # Add the data from SQLite

    # Clear the existing sheet (except the header row) and update with new data
    activity_sheet.clear()
    activity_sheet.update('A1', rows_to_update)

    # Close the connection
    conn.close()
    print("Google sheet updated")