import gspread
import os
from dotenv import load_dotenv
import sqlite3
import discord
from discord.ext import commands

load_dotenv()

def update_google_sheet():
     Google Sheet initialization
    spreadsheet_ID = os.environ.get('SPREADSHEET_ID')
    gc = gspread.service_account(filename='wmac_key.json')
    sh = gc.open_by_key(spreadsheet_ID)
    activity_sheet = sh.worksheet('Activity')
    conn = sqlite3.connect('db/wm_db.sqlite')
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(Tracker)")
    columns = [info[1] for info in cursor.fetchall()][1:]  
    cursor.execute("SELECT user_role, user_name, nick_name, last_activity_date, days_inactive, maps_participated_in, maps_won, maps_lost, notes FROM Tracker")
    data = cursor.fetchall()
    rows_to_update = [columns]  
    rows_to_update.extend(data)  
    activity_sheet.clear()
    activity_sheet.update('A1', rows_to_update)
    conn.close()
    print("Google sheet updated")

async def change_channel_category(interaction, new_category_id):
    new_category = discord.utils.get(interaction.guild.categories, id=new_category_id)
    channel = interaction.channel
    if new_category:
        await channel.edit(category=new_category)