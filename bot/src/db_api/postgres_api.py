from dotenv import load_dotenv
from prisma import Prisma
import asyncio

load_dotenv()

async def main():
    prisma = Prisma()
    await prisma.connect()
    user=await prisma.user.find_first()
    print(user)
    print(user.id)
    await prisma.disconnect()