import discord
from discord.ext import commands
from shared_assets.shared import update_google_sheet
from dotenv import load_dotenv
import sqlite3
from discord import app_commands
from datetime import datetime
from scope import DiscordID
load_dotenv()

class Scheduler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('db/wm_db.sqlite')


    @app_commands.command(name="makeprivate", description="Makes the channel private except for five specific users")
    async def makeprivate(self, interaction: discord.Interaction, 
                           ally1: discord.Member, 
                           ally2: discord.Member = None, 
                           ally3: discord.Member = None, 
                           ally4: discord.Member = None):

        channel = interaction.channel
        leader = interaction.user
        
        # Get the nick or name, handle None values for optional allies
        leader_id = leader.id
        ally1_id = ally1.id
        ally2_id = ally2.id if ally2 else None
        ally3_id = ally3.id if ally3 else None
        ally4_id = ally4.id if ally4 else None
        
        # Execute the SQLite command
        self.conn.execute("""
                        UPDATE GAMES SET leader = ?, ally1 = ?, ally2 = ?, ally3 = ?, ally4 = ? 
                        WHERE channel_id = ?""",
                        (leader_id, ally1_id, ally2_id, ally3_id, ally4_id, channel.id))
        self.conn.commit()
        allowed_members = [leader, ally1, ally2, ally3, ally4]
        allowed_members = [member for member in allowed_members if member is not None]  # Fixed filtering condition
        # Overwrite permissions for members not in the allowed list
        try:
            for member in channel.members:
                if member not in allowed_members and not member.guild_permissions.administrator and not member.bot:
                    await channel.set_permissions(member, read_messages=False, send_messages=False)
        except Exception as e:
            print(f"An error occurred: {e}")
        # Grant access to the specified members
        try:
            with self.conn:
                cursor = self.conn.cursor()

                cursor.execute("UPDATE Tracker SET maps_led = maps_led + 1 WHERE user_name = ?", 
                               (leader.name,))  # Ensure the parameter is a tuple
                for member in allowed_members:
                    query = "UPDATE Tracker SET last_activity_date = ?, maps_participated_in = maps_participated_in + 1 WHERE user_name = ?"
                    params = (datetime.today().strftime('%Y-%m-%d'), member.name)
                    cursor.execute(query, params) 
        except Exception as e:
            print(f"An error occurred: {e}")
        try:
            await interaction.response.send_message("Channel is now private except for the specified members and admin.")
        except Exception as e:
            print("channel now private", e)

    @app_commands.command(name="maplaunch", description="Launch a map with the selected game mode")
    async def maplaunch(self, interaction: discord.Interaction):
        channel_id = interaction.channel.id
        cursor = self.conn.execute("SELECT leader, ally1, ally2, ally3, ally4 FROM games WHERE channel_id = ?", (channel_id,))
        result = cursor.fetchone()
        if result is None:
            await interaction.response.send_message("No game data found for this channel.", ephemeral=True)
            return
        user_ids = [user_id for user_id in result if user_id]
        formatted_user_ids = [f'<@{user_id}>' for user_id in user_ids]
        mention_message = "A new game has started with " + ', '.join(formatted_user_ids[:-1]) + ' and ' + formatted_user_ids[-1]
        await interaction.guild.get_channel(DiscordID.test_public_notif_channel).send(mention_message)
        await interaction.response.send_message(f"Launching game good luck!")

    @app_commands.command(name="mapend", description="End match")
    @app_commands.choices(
        result=[
            app_commands.Choice(name="Win", value="win"),
            app_commands.Choice(name="Lose", value="lose")
        ]
    )
    async def mapend(self, interaction: discord.Interaction, result: str):
        channel = interaction.channel
        if result == "win":
            channel_id = interaction.channel.id
            cursor = self.conn.execute("SELECT leader, ally1, ally2, ally3, ally4 FROM games WHERE channel_id = ?", (channel_id,))
            people = cursor.fetchone()
            if people is None:
                await interaction.response.send_message("No game data found for this channel.", ephemeral=True)
                return
            user_ids = [user_id for user_id in people if user_id]
            formatted_user_ids = [f'<@{user_id}>' for user_id in user_ids]
            mention_message = "A game has been won by " + ', '.join(formatted_user_ids[:-1]) + ' and ' + formatted_user_ids[-1]
            new_category_id = DiscordID.test_victory_category
            new_category = discord.utils.get(interaction.guild.categories, id=new_category_id)
            if new_category:
                await channel.edit(category=new_category)
            await channel.set_permissions(interaction.guild.default_role, read_messages=True, send_messages=True)
            await interaction.guild.get_channel(DiscordID.test_public_notif_channel).send(mention_message)
            await interaction.response.send_message("congrats")

        
        elif result == "lose":
            # Delete the channel
            try:
                await channel.delete()
                await interaction.response.send_message('ew')
            except Exception as e:
                print(e)

    def cog_unload(self):
        self.conn.close()

# Set up the cog
async def setup(bot):
    await bot.add_cog(Scheduler(bot))
