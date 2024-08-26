import discord
from datetime import datetime

class YearDropdown(discord.ui.Select):
    def __init__(self, cog):
        current_year = datetime.now().year
        options = [discord.SelectOption(label=str(year), value=str(year)) for year in range(current_year, current_year + 5)]
        super().__init__(placeholder="Select a year", min_values=1, max_values=1, options=options)
        self.cog = cog

    async def callback(self, interaction: discord.Interaction):
        selected_year = self.values[0]
        self.cog.responses['year'] = selected_year
        await interaction.response.edit_message(content=f"Year selected: {selected_year}. Now select a month.", view=MonthView(self.cog))

class MonthDropdown(discord.ui.Select):
    def __init__(self, cog):
        options = [discord.SelectOption(label=month, value=str(index + 1)) for index, month in enumerate([
            "January", "February", "March", "April", "May", "June", 
            "July", "August", "September", "October", "November", "December"])]
        super().__init__(placeholder="Select a month", min_values=1, max_values=1, options=options)
        self.cog = cog

    async def callback(self, interaction: discord.Interaction):
        selected_month = self.values[0]
        self.cog.responses['month'] = selected_month
        await interaction.response.edit_message(content=f"Month selected: {selected_month}. Now select a day.", view=DayView(self.cog))

class DayDropdown(discord.ui.Select):
    def __init__(self, cog):
        year = int(cog.responses['year'])
        month = int(cog.responses['month'])
        days_in_month = (datetime(year, month + 1, 1) - datetime(year, month, 1)).days
        options = [discord.SelectOption(label=str(day)) for day in range(1, days_in_month + 1)]
        super().__init__(placeholder="Select a day", min_values=1, max_values=1, options=options)
        self.cog = cog

    async def callback(self, interaction: discord.Interaction):
        selected_day = self.values[0]
        self.cog.responses['day'] = selected_day
        await interaction.response.edit_message(content=f"Date selected: {self.cog.responses['year']}-{self.cog.responses['month']}-{selected_day}", view=None)

class DateSelectionView(discord.ui.View):
    def __init__(self, cog):
        super().__init__()
        self.cog = cog
        self.add_item(YearDropdown(self.cog))

class MonthView(discord.ui.View):
    def __init__(self, cog):
        super().__init__()
        self.cog = cog
        self.add_item(MonthDropdown(self.cog))

class DayView(discord.ui.View):
    def __init__(self, cog):
        super().__init__()
        self.cog = cog
        self.add_item(DayDropdown(self.cog))

class DateQuestionView(discord.ui.View):
    def __init__(self, cog):
        super().__init__()
        self.cog = cog

    @discord.ui.button(label="Select Date", style=discord.ButtonStyle.success, custom_id="select_date")
    async def select_date_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        date_view = DateSelectionView(self.cog)
        await interaction.response.edit_message(content="Please select a year:", view=date_view)

# Example of starting the date question
class MakeMap(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.responses = {}

    @app_commands.command(name="makemap", description="Ask question to start pregame lobby")
    async def makemap(self, interaction: discord.Interaction):
        first_view = DateQuestionView(self)
        await interaction.response.send_message("Do you want to pick a date?", view=first_view)

# Set up the cog
async def setup(bot):
    await bot.add_cog(MakeMap(bot))
