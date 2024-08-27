import discord
from discord import app_commands
from discord.ext import commands
from scope import DiscordID
import sqlite3

# rules question
class RolesQuestionView(discord.ui.View):
    def __init__(self, cog):
        super().__init__()
        self.cog = cog
    @discord.ui.button(label="Yes", style=discord.ButtonStyle.success, custom_id="yes")
    async def option_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        second_view = LeaderQuestionView(self.cog)
        await interaction.response.edit_message(content="Are you comfortable being vocal and leading your team?", view=second_view)

    @discord.ui.button(label="No", style=discord.ButtonStyle.danger, custom_id="no")
    async def option_2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content=f"Please review how roles work and come back. <#{DiscordID.test_roles_tutorial}>", view=None)

# leading question
class LeaderQuestionView(discord.ui.View):
    def __init__(self, cog):
        super().__init__()
        self.cog = cog

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.success, custom_id="yes")
    async def option_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        third_view = RulesQuestionView(self.cog)
        await interaction.response.edit_message(content="Do you understand how to summarize the Map Registration before the game and swear to provide a fair and honest Field Report at the end of the game?", view=third_view)

    @discord.ui.button(label="No", style=discord.ButtonStyle.danger, custom_id="no")
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content=f"Here is a channel to help you find leader<#{DiscordID.test_new_map_chat}>", view=None)

# sumerize question
class RulesQuestionView(discord.ui.View):
    def __init__(self, cog):
        super().__init__()
        self.cog = cog

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.success, custom_id="yes")
    async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            dropdown_view = TimeoutError(self.cog)
            await interaction.response.edit_message(content="Select when the event starts:", view=dropdown_view)
        except Exception as e:
            print(e)

    @discord.ui.button(label="No", style=discord.ButtonStyle.danger, custom_id="no")
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content=f"Please review how to lead and come back <#{DiscordID.test_how_to_lead}>", view=None)



class TimerView(discord.ui.View):
    def __init__(self, cog):
        super().__init__()
        self.cog = cog
        
        hour_options = [discord.SelectOption(label=f"{hour:02}", description=f"{hour:02}:00 or {hour:02}:30") for hour in range(24)]
        self.hour_select = discord.ui.Select(placeholder="Select hour", options=hour_options, min_values=1, max_values=1)
        self.hour_select.callback = self.hour_select_callback
        self.add_item(self.hour_select)
        
        minute_options = [discord.SelectOption(label=f"{minute:02}", description="Minutes") for minute in [0, 15, 30, 45]]
        self.minute_select = discord.ui.Select(placeholder="Select minute", options=minute_options, min_values=1, max_values=1)
        self.minute_select.callback = self.minute_select_callback
        self.add_item(self.minute_select)

    async def hour_select_callback(self, interaction: discord.Interaction):
        selected_hour = self.hour_select.values[0]
        self.cog.responses['hour'] = selected_hour
        
        if 'minute' in self.cog.responses:
            await self.process_time(interaction)

    async def minute_select_callback(self, interaction: discord.Interaction):
        selected_minute = self.minute_select.values[0]
        self.cog.responses['minute'] = selected_minute
        
        if 'hour' in self.cog.responses:
            await self.process_time(interaction)
    
    async def process_time(self, interaction: discord.Interaction):
        time = f"{self.cog.responses['hour']}:{self.cog.responses['minute']}"
        self.cog.responses['time'] = time
        dropdown_view = DropdownViewMap(self.cog)
        await interaction.response.edit_message(content="Select map:", view=dropdown_view)



# drop down for what map
class DropdownMap(discord.ui.Select):
    def __init__(self, cog):
        self.cog = cog
        cursor = self.cog.conn.execute("SELECT DISTINCT(game_type) FROM REGIONS")
        game_types = cursor.fetchall()
        options = [discord.SelectOption(label=game[0]) for game in game_types]
        super().__init__(placeholder="Please pick a map (scrollable)", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_option = self.values[0]
        self.cog.responses["map"] = selected_option
        forth_view = ForthQuestionView(self.cog)
        await interaction.response.edit_message(content="What speed?", view=forth_view)

class DropdownViewMap(discord.ui.View):
    def __init__(self, cog):
        super().__init__()
        self.cog = cog
        self.add_item(DropdownMap(self.cog))

# speed question
class ForthQuestionView(discord.ui.View):
    def __init__(self, cog):
        super().__init__()
        self.cog = cog

    @discord.ui.button(label="1x", style=discord.ButtonStyle.success, custom_id="1x")
    async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        dropdown_view = DropdownViewRegion(self.cog)
        self.cog.responses['speed'] = "1x"
        await interaction.response.edit_message(content="Please choose an option from the dropdown menu:", view=dropdown_view)

    @discord.ui.button(label="4x", style=discord.ButtonStyle.success, custom_id="4x")
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.cog.responses['speed'] = "4x"
        dropdown_view = DropdownViewRegion(self.cog)
        await interaction.response.edit_message(content="Please choose an option from the dropdown menu:", view=dropdown_view)

# drop down for what region
class DropdownRegion(discord.ui.Select):
    def __init__(self, cog):
        self.cog = cog
        cursor = self.cog.conn.execute("SELECT DISTINCT(region) FROM REGIONS WHERE game_type = ?", (self.cog.responses["map"],))
        regions = cursor.fetchall()
        options = [discord.SelectOption(label=region[0]) for region in regions]
        super().__init__(placeholder="Please pick a region (scrollable)", min_values=1, max_values=1, options=options)
    async def callback(self, interaction: discord.Interaction):
        try:
            selected_option = self.values[0]
            self.cog.responses['region'] = selected_option
            cursor = self.cog.conn.execute("SELECT territory FROM REGIONS WHERE game_type = ? and region = ?",(self.cog.responses['map'],self.cog.responses['region']))
            territorys = cursor.fetchall()
            message1 = f'__**{self.cog.responses["region"]}**__\n'
            message2 = '\n'.join([territory[0] for territory in territorys])
            message = message1 + message2
            category_id = DiscordID.test_pregame_lobbies  
            category = interaction.guild.get_channel(category_id)

            if category is None or not isinstance(category, discord.CategoryChannel):
                await interaction.response.send_message("The category could not be found or is not valid.", ephemeral=True)
                return
            map_word = self.cog.responses["map"].split(' ')[0]
            if self.cog.responses['map'] == "Battleground USA Regions (max 3 players)":
                map_word = "Battleground USA"
            elif self.cog.responses['map']=="Rising Tides Regions (max 3 players)":
                map_word = "Rising Tides"
            channel_name = f'{self.cog.responses["region"]}-{self.cog.responses["speed"]}-{map_word}-{self.cog.responses["username"]}'
            if self.cog.responses["map"] == "WW3 Regions (5 players max)" and self.cog.responses["speed"] == "4x":
                channel_name = f'{self.cog.responses["region"]}-{self.cog.responses["speed"]}-{self.cog.responses["username"]}'
                
            new_channel = await category.create_text_channel(name=channel_name)
            new_id = new_channel.id
            conn = sqlite3.connect('db/wm_db.sqlite')
            conn.execute("""
            INSERT INTO GAMES (channel_id, region, map, speed)
            VALUES (?, ?, ?, ?)
            """, (new_id, self.cog.responses["region"], self.cog.responses["map"], self.cog.responses["speed"]))
            conn.commit()
            await new_channel.send(f"<#{DiscordID.test_roles_tutorial}>")
            await new_channel.send("Military Role Request -\nPrimary Country Selection -\nSecondary Country Selection-")
            await new_channel.send(f"{message}")
            await interaction.response.edit_message(content = f"Channel '<#{new_id}>' has been created", view = None)
        except Exception as e:
            print(e)

class DropdownViewRegion(discord.ui.View):
    def __init__(self, cog):
        super().__init__()
        self.cog = cog
        self.add_item(DropdownRegion(self.cog))
# cog that starts the thing
class MakeMap(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.responses = {}
        self.conn = sqlite3.connect('db/wm_db.sqlite')

    @app_commands.command(name="makemap", description="Ask question to start pregame lobby")
    async def makemap(self, interaction: discord.Interaction):
        username = interaction.user.nick or interaction.user.name
        self.responses['username'] = username
        first_view = RolesQuestionView(self)
        await interaction.response.send_message("Are you familiar with our roles?", view=first_view)

# Set up the cog
async def setup(bot):
    await bot.add_cog(MakeMap(bot))
