from dotenv import load_dotenv
from prisma import Prisma
import asyncio

load_dotenv()


async def get_user_test():
    prisma = Prisma()
    await prisma.connect()
    user = await prisma.user.find_first()
    await prisma.disconnect()
    return {
        "id": user.id,
        "name": user.name,
        "info": user.info
    }
