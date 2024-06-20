# discord.pyの大事な部分をimport
from discord.ext import commands
import discord
import os
import asyncio
from dotenv import load_dotenv
from db_api import get_user_test

load_dotenv(".env")

# デプロイ先の環境変数にトークンをおいてね
API_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
# botのオブジェクトを作成(コマンドのトリガーを!に)
bot = commands.Bot(command_prefix="/", intents=discord.Intents.all(),
                   application_id=os.environ["APPLICATION_ID"],)


# イベントを検知
@bot.event
# botの起動が完了したとき
async def on_ready():
    await bot.tree.sync()
    print("Hello!")  # コマンドラインにHello!と出力


async def main():
    print(await get_user_test())
    # コグのフォルダ
    cog_folder = "cogs."
    # そして使用するコグの列挙(拡張子無しのファイル名)
    cogs = ["sample_cog", "main_cog"]

    for c in cogs:
        await bot.load_extension(cog_folder + c)
    print("Bot is ready!")
    # start the client
    async with bot:
        await bot.start(API_TOKEN)

asyncio.run(main())
