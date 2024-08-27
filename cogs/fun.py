import discord
from discord.ext import commands
from discord import app_commands

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="map", description="Sends the map image")
    async def map(self, ctx: commands.Context):
        image_url = 'https://cdn.discordapp.com/attachments/1047042927429427253/1275413510683103334/IMG_4488.jpg?ex=66c5cce4&is=66c47b64&hm=7357f0a270dcfa9d10bdbab02fae90d866e393984d270dd53da53ea3f4bb9799&'
        await ctx.send(image_url)

async def setup(bot):
    await bot.add_cog(Fun(bot))
