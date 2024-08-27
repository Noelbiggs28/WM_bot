import discord
from discord.ext import commands, tasks
from shared_assets.shared import update_google_sheet
from dotenv import load_dotenv
from scope import DiscordID, Messages
from datetime import datetime
import sqlite3
import os
import asyncio
load_dotenv()


class HeadCounter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.category_counts = {'1x': 0, '4x': 0, 'channel_1x': 0, 'channel_4x': 0}
        self.daily_task.start()
        self.conn = sqlite3.connect('db/wm_db.sqlite')


    @commands.command(
        name="initialize_members",
        description="Initial startup for member activity tracking"
    )
    @commands.guild_only()
    async def initialize_members(self, ctx):
        await ctx.defer()
        updated_users = 0
        members = ctx.guild.members
        insert_query = """
        INSERT OR REPLACE INTO TRACKER (user_role, user_name, nick_name, last_activity_date, days_inactive, maps_participated_in, maps_led, maps_won, maps_lost)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        cursor = self.conn.cursor()

        for member in members:
            if member.bot:
                continue
            updated_users += 1
            user_role = 'starter'
            print(member.roles)
            if DiscordID.test_veteran in member.roles:
                user_role = 'veteran'
                break
            row_data = (
                user_role,
                member.name,
                member.nick or '',  
                datetime.today().strftime('%Y-%m-%d'),
                0,  # Days inactive
                0,  # Maps participated in
                0,  # Maps led
                0,  # Maps won
                0   # Maps lost
            )
            cursor.execute(insert_query, row_data)
        self.conn.commit()  
        cursor.close()

        await ctx.send(f'Member initialization complete. Collected total {updated_users} users')


    @commands.command(
        name="manual_update",
        description="Copys database to gs"
    )
    @commands.guild_only()
    async def manual_update(self, ctx):
        update_google_sheet()
        await ctx.send(f'Google sheet updated')

    def update_days_inactive(self):
        self.conn.execute("""
            UPDATE TRACKER
            SET days_inactive = CAST(julianday('now') - julianday(last_activity_date) AS INTEGER)
        """)
        self.conn.commit()
        print("Days inactive updated based on last activity date.")


    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        username = after.name
        roles_before = [role.id for role in before.roles]
        roles_after = [role.id for role in after.roles]
        print(roles_before)
        print(roles_after)
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Tracker WHERE user_name = ?", (username,))
        user_data = cursor.fetchone()
        if DiscordID.test_veteran in roles_after:
            if user_data:
                cursor.execute("UPDATE Tracker SET user_role = ? WHERE user_name = ?", ('veteran', username))
                self.conn.commit()

        elif DiscordID.test_private in roles_after or DiscordID.test_greenie in roles_after:
            if DiscordID.test_private not in roles_before and DiscordID.test_greenie not in roles_before:
                if user_data:
                    cursor.execute("UPDATE Tracker SET user_role = ? WHERE user_name = ?", ('starter', username))
                else:
                    cursor.execute("""
                        INSERT INTO Tracker (user_role, user_name, nick_name, last_activity_date, days_inactive, maps_participated_in, maps_led, maps_won, maps_lost)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, ('starter', username, after.nick or '', datetime.today().strftime('%Y-%m-%d'), 0, 0, 0, 0, 0))
                self.conn.commit()
        update_google_sheet()

    @commands.command(
        name="initialize_channel",
        description="Initial startup for channel count tracking"
    )
    @commands.guild_only()
    async def initialize_channel(self, ctx):
        await ctx.defer()
        self.category_counts['1x'] = 0
        self.category_counts['4x'] = 0

        channels = ctx.guild.channels
        for channel in channels:
            if channel.category is None:
                continue
            if channel.category.id == DiscordID.test_category_1x:
                self.category_counts['1x'] += 1
            elif channel.category.id == DiscordID.test_category_4x:
                self.category_counts['4x'] += 1

        channel_1x_name = f'{Messages.channel_name}{self.category_counts["1x"]}'
        channel_4x_name = f'{Messages.channel_name}{self.category_counts["4x"]}'
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(connect=False)
        }

        channel_1x = await ctx.guild.create_voice_channel(channel_1x_name,
                                                          position=1,
                                                          category=ctx.guild.get_channel(DiscordID.test_category_1x),
                                                          overwrites=overwrites)
        channel_4x = await ctx.guild.create_voice_channel(channel_4x_name,
                                                          position=1,
                                                          category=ctx.guild.get_channel(DiscordID.test_category_4x),
                                                          overwrites=overwrites)

        self.category_counts['channel_1x'] = channel_1x.id
        self.category_counts['channel_4x'] = channel_4x.id

        await ctx.send('Channel count creation complete')


    @tasks.loop(hours=24)
    async def daily_task(self):
        pass
        # self.update_days_inactive()
        # update_google_sheet()

    @daily_task.before_loop
    async def before_daily_task(self):
        await self.bot.wait_until_ready()
        # while True:
        #     now = datetime.datetime.now()
        #     if now.hour == 23:
        #         break
        #     await asyncio.sleep(3600)  

async def setup(bot):
    await bot.add_cog(HeadCounter(bot))
