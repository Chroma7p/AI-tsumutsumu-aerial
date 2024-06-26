import asyncio
from prisma import Prisma


async def main():
    prisma = Prisma()
    await prisma.connect()

    # Create Users
    user1 = await prisma.user.create(
        data={
            'id': 'user1',
            'name': 'Alice',
            'info': 'Admin user',
        },
    )

    user2 = await prisma.user.create(
        data={
            'id': 'user2',
            'name': 'Bob',
            'info': 'Regular user',
        },
    )

    user3 = await prisma.user.create(
        data={
            'id': 'user3',
            'name': 'Charlie',
            'info': None,  # No info provided
        },
    )

    user4 = await prisma.user.create(
        data={
            'id': 'user4',
            'name': 'Diana',
            'info': 'Guest user',
        },
    )

    # Create Guilds
    guild1 = await prisma.guild.create(
        data={
            'id': 'guild1',
            'name': 'Guild One',
            'info': 'This is Guild One',
        },
    )

    guild2 = await prisma.guild.create(
        data={
            'id': 'guild2',
            'name': 'Guild Two',
            'info': 'This is Guild Two',
        },
    )

    guild3 = await prisma.guild.create(
        data={
            'id': 'guild3',
            'name': 'Guild Three',
            'info': None,  # No info provided
        },
    )

    # Create Channels
    channel1 = await prisma.channel.create(
        data={
            'id': 'channel1',
            'name': 'General',
            'info': 'General chat channel',
            'guildId': guild1.id,
        },
    )

    channel2 = await prisma.channel.create(
        data={
            'id': 'channel2',
            'name': 'Random',
            'info': 'Random chat channel',
            'guildId': guild1.id,
        },
    )

    channel3 = await prisma.channel.create(
        data={
            'id': 'channel3',
            'name': 'Announcements',
            'info': 'Announcements channel',
            'guildId': guild2.id,
        },
    )

    channel4 = await prisma.channel.create(
        data={
            'id': 'channel4',
            'name': 'Help',
            'info': 'Help channel',
            'guildId': guild3.id,
        },
    )

    channel5 = await prisma.channel.create(
        data={
            'id': 'channel5',
            'name': 'Off-Topic',
            'info': None,  # No info provided
            'guildId': guild2.id,
        },
    )

    # Create UserGuild relations
    await prisma.userguild.create_many(
        data=[
            {'userId': user1.id, 'guildId': guild1.id},
            {'userId': user2.id, 'guildId': guild1.id},
            {'userId': user1.id, 'guildId': guild2.id},
            {'userId': user3.id, 'guildId': guild1.id},
            {'userId': user3.id, 'guildId': guild2.id},
            {'userId': user4.id, 'guildId': guild3.id},
            {'userId': user2.id, 'guildId': guild3.id},
        ],
    )

    # Create Emoji
    emoji1 = await prisma.emoji.create(
        data={
            'id': 'emoji1',
            'name': 'smile',
            'info': 'Smile emoji',
            'guildId': guild1.id,
        },
    )

    print('Seeding completed.')

    await prisma.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
