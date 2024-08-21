import discord
from discord.ext import commands, tasks
import datetime
import pytz
import asyncio

from channels import TEST_GUILD_IDS

class TimeZones(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # [timezone for grabbing time, words to add to channel, channel id, if it observes dst]
        self.channel_ids = TEST_GUILD_IDS
        self.update_channels_task.start() 

    @tasks.loop(minutes=5)  # Update every 5 minutes
    async def update_channels_task(self):
        print("Updating channel names...")
        self.time_in()

    def time_in(self):
        for channel in self.channel_ids:
            try:
                timezone = pytz.timezone(channel[0])
                current_time = datetime.datetime.now(timezone)
                is_dst = bool(current_time.dst())
                hours = f"{current_time.hour:02}"
                minutes = f"{current_time.minute:02}"
                channel_words=""
                if channel[3]:
                    if is_dst:
                        channel_words = channel[1][0]
                    else:
                        channel_words = channel[1][1]
                else:
                    channel_words=channel[1]
                name = f"{hours}{minutes} {channel_words}"
                self.bot.loop.create_task(self.rename_channel(channel[2], name))
            except Exception as e:
                print(f"Error updating channel {channel[1]}: {e}")

    async def rename_channel(self, channel_id: int, new_name: str):
        channel = self.bot.get_channel(channel_id)
        if isinstance(channel, discord.VoiceChannel):
            await channel.edit(name=new_name)
        else:
            print(f"Channel with ID {channel_id} is not a voice channel.")

    @update_channels_task.before_loop
    async def before_update(self):
        await self.bot.wait_until_ready()  

        # Wait until the current time's minute is a multiple of 5
        while True:
            now = datetime.datetime.now()
            if now.minute % 5 == 0:
                break
            await asyncio.sleep(30)  

# Register the cog
async def setup(bot):
    await bot.add_cog(TimeZones(bot))
