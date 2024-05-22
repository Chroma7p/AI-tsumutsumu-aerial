from discord.ext import commands, tasks
from discord import app_commands
import discord
from channel import Channel


class MainCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.channels: dict[str, Channel] = dict()

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.tree.sync()
        print("MainCog is ready!")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        print(f"message: {message.content}")
        if message.author == self.bot.user:
            return
        try:
            if message.channel.id not in self.channels:
                self.channels[message.channel.id] = Channel(
                    self.bot, message.channel.id)
            channel = self.channels[message.channel.id]
            msg = await message.reply("考え中...")
            txt = ""
            for s in channel.chat.send_stream(message.content):
                txt += s
                if len(txt) % 5 == 0:
                    await msg.edit(content=txt)
            await msg.edit(content=txt)
        except Exception as e:
            print(e.with_traceback())

            await message.reply("エラーが発生しました。")


async def setup(bot: commands.Bot):
    await bot.add_cog(MainCog(bot))
