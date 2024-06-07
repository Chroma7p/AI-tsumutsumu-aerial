-- CreateTable
CREATE TABLE "Guild" (
    "discord_id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "info" TEXT,

    CONSTRAINT "Guild_pkey" PRIMARY KEY ("discord_id")
);

-- CreateTable
CREATE TABLE "Channel" (
    "discord_id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "info" TEXT,

    CONSTRAINT "Channel_pkey" PRIMARY KEY ("discord_id")
);

-- CreateTable
CREATE TABLE "User" (
    "discord_id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "info" TEXT,

    CONSTRAINT "User_pkey" PRIMARY KEY ("discord_id")
);

-- CreateTable
CREATE TABLE "GuildChannel" (
    "guildId" TEXT NOT NULL,
    "channelId" TEXT NOT NULL,

    CONSTRAINT "GuildChannel_pkey" PRIMARY KEY ("guildId","channelId")
);

-- CreateTable
CREATE TABLE "GuildUser" (
    "guildId" TEXT NOT NULL,
    "userId" TEXT NOT NULL,

    CONSTRAINT "GuildUser_pkey" PRIMARY KEY ("guildId","userId")
);

-- CreateIndex
CREATE UNIQUE INDEX "Guild_discord_id_key" ON "Guild"("discord_id");

-- CreateIndex
CREATE UNIQUE INDEX "Channel_discord_id_key" ON "Channel"("discord_id");

-- CreateIndex
CREATE UNIQUE INDEX "User_discord_id_key" ON "User"("discord_id");

-- AddForeignKey
ALTER TABLE "GuildChannel" ADD CONSTRAINT "GuildChannel_guildId_fkey" FOREIGN KEY ("guildId") REFERENCES "Guild"("discord_id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "GuildChannel" ADD CONSTRAINT "GuildChannel_channelId_fkey" FOREIGN KEY ("channelId") REFERENCES "Channel"("discord_id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "GuildUser" ADD CONSTRAINT "GuildUser_guildId_fkey" FOREIGN KEY ("guildId") REFERENCES "Guild"("discord_id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "GuildUser" ADD CONSTRAINT "GuildUser_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("discord_id") ON DELETE RESTRICT ON UPDATE CASCADE;
