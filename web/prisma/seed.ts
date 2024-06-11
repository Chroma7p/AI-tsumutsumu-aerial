import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
    // Create Users
    const user1 = await prisma.user.create({
        data: {
            id: 'user1',
            name: 'Alice',
            info: 'Admin user',
        },
    });

    const user2 = await prisma.user.create({
        data: {
            id: 'user2',
            name: 'Bob',
            info: 'Regular user',
        },
    });

    const user3 = await prisma.user.create({
        data: {
            id: 'user3',
            name: 'Charlie',
            info: null, // No info provided
        },
    });

    const user4 = await prisma.user.create({
        data: {
            id: 'user4',
            name: 'Diana',
            info: 'Guest user',
        },
    });

    // Create Guilds
    const guild1 = await prisma.guild.create({
        data: {
            id: 'guild1',
            name: 'Guild One',
            info: 'This is Guild One',
        },
    });

    const guild2 = await prisma.guild.create({
        data: {
            id: 'guild2',
            name: 'Guild Two',
            info: 'This is Guild Two',
        },
    });

    const guild3 = await prisma.guild.create({
        data: {
            id: 'guild3',
            name: 'Guild Three',
            info: null, // No info provided
        },
    });

    // Create Channels
    const channel1 = await prisma.channel.create({
        data: {
            id: 'channel1',
            name: 'General',
            info: 'General chat channel',
            guildId: guild1.id,
        },
    });

    const channel2 = await prisma.channel.create({
        data: {
            id: 'channel2',
            name: 'Random',
            info: 'Random chat channel',
            guildId: guild1.id,
        },
    });

    const channel3 = await prisma.channel.create({
        data: {
            id: 'channel3',
            name: 'Announcements',
            info: 'Announcements channel',
            guildId: guild2.id,
        },
    });

    const channel4 = await prisma.channel.create({
        data: {
            id: 'channel4',
            name: 'Help',
            info: 'Help channel',
            guildId: guild3.id,
        },
    });

    const channel5 = await prisma.channel.create({
        data: {
            id: 'channel5',
            name: 'Off-Topic',
            info: null, // No info provided
            guildId: guild2.id,
        },
    });

    // Create UserGuild relations
    await prisma.userGuild.createMany({
        data: [
            { userId: user1.id, guildId: guild1.id },
            { userId: user2.id, guildId: guild1.id },
            { userId: user1.id, guildId: guild2.id },
            { userId: user3.id, guildId: guild1.id },
            { userId: user3.id, guildId: guild2.id },
            { userId: user4.id, guildId: guild3.id },
            { userId: user2.id, guildId: guild3.id },
        ],
    });

    // Create Emoji 
    const emoji1 = await prisma.emoji.create({
        data: {
            id: 'emoji1',
            name: 'smile',
            info: 'Smile emoji',
            guildId: guild1.id,
        },
    });



    console.log('Seeding completed.');
}

main()
    .catch(e => {
        console.error(e);
        process.exit(1);
    })
    .finally(async () => {
        await prisma.$disconnect();
    });
