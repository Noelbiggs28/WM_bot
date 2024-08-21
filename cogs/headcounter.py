import discord
from discord.ext import commands

class HeadCounter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()  
    async def get_nicknames(self, ctx):
        guild = ctx.guild  
        nicknames = [member.nick or member.name for member in guild.members if not member.bot] 
        nicknames_list = "\n".join(nicknames)
        await ctx.send(f"Nicknames in the server:\n{nicknames_list}")

# Setup function to add the cog to the bot
async def setup(bot):
    await bot.add_cog(HeadCounter(bot))
