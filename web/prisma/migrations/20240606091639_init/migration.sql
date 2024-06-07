/*
  Warnings:

  - The primary key for the `Channel` table will be changed. If it partially fails, the table could be left without primary key constraint.
  - You are about to drop the column `discord_id` on the `Channel` table. All the data in the column will be lost.
  - The primary key for the `Guild` table will be changed. If it partially fails, the table could be left without primary key constraint.
  - You are about to drop the column `discord_id` on the `Guild` table. All the data in the column will be lost.
  - The primary key for the `User` table will be changed. If it partially fails, the table could be left without primary key constraint.
  - You are about to drop the column `discord_id` on the `User` table. All the data in the column will be lost.
  - You are about to drop the `GuildChannel` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `GuildUser` table. If the table is not empty, all the data it contains will be lost.
  - Added the required column `guildId` to the `Channel` table without a default value. This is not possible if the table is not empty.
  - The required column `id` was added to the `Channel` table with a prisma-level default value. This is not possible if the table is not empty. Please add this column as optional, then populate it before making it required.
  - The required column `id` was added to the `Guild` table with a prisma-level default value. This is not possible if the table is not empty. Please add this column as optional, then populate it before making it required.
  - The required column `id` was added to the `User` table with a prisma-level default value. This is not possible if the table is not empty. Please add this column as optional, then populate it before making it required.

*/
-- DropForeignKey
ALTER TABLE "GuildChannel" DROP CONSTRAINT "GuildChannel_channelId_fkey";

-- DropForeignKey
ALTER TABLE "GuildChannel" DROP CONSTRAINT "GuildChannel_guildId_fkey";

-- DropForeignKey
ALTER TABLE "GuildUser" DROP CONSTRAINT "GuildUser_guildId_fkey";

-- DropForeignKey
ALTER TABLE "GuildUser" DROP CONSTRAINT "GuildUser_userId_fkey";

-- DropIndex
DROP INDEX "Channel_discord_id_key";

-- DropIndex
DROP INDEX "Guild_discord_id_key";

-- DropIndex
DROP INDEX "User_discord_id_key";

-- AlterTable
ALTER TABLE "Channel" DROP CONSTRAINT "Channel_pkey",
DROP COLUMN "discord_id",
ADD COLUMN     "guildId" TEXT NOT NULL,
ADD COLUMN     "id" TEXT NOT NULL,
ADD CONSTRAINT "Channel_pkey" PRIMARY KEY ("id");

-- AlterTable
ALTER TABLE "Guild" DROP CONSTRAINT "Guild_pkey",
DROP COLUMN "discord_id",
ADD COLUMN     "id" TEXT NOT NULL,
ADD CONSTRAINT "Guild_pkey" PRIMARY KEY ("id");

-- AlterTable
ALTER TABLE "User" DROP CONSTRAINT "User_pkey",
DROP COLUMN "discord_id",
ADD COLUMN     "id" TEXT NOT NULL,
ADD CONSTRAINT "User_pkey" PRIMARY KEY ("id");

-- DropTable
DROP TABLE "GuildChannel";

-- DropTable
DROP TABLE "GuildUser";

-- CreateTable
CREATE TABLE "UserGuild" (
    "userId" TEXT NOT NULL,
    "guildId" TEXT NOT NULL,

    CONSTRAINT "UserGuild_pkey" PRIMARY KEY ("userId","guildId")
);

-- CreateTable
CREATE TABLE "_UserGuilds" (
    "A" TEXT NOT NULL,
    "B" TEXT NOT NULL
);

-- CreateIndex
CREATE UNIQUE INDEX "_UserGuilds_AB_unique" ON "_UserGuilds"("A", "B");

-- CreateIndex
CREATE INDEX "_UserGuilds_B_index" ON "_UserGuilds"("B");

-- AddForeignKey
ALTER TABLE "Channel" ADD CONSTRAINT "Channel_guildId_fkey" FOREIGN KEY ("guildId") REFERENCES "Guild"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "UserGuild" ADD CONSTRAINT "UserGuild_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "UserGuild" ADD CONSTRAINT "UserGuild_guildId_fkey" FOREIGN KEY ("guildId") REFERENCES "Guild"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_UserGuilds" ADD CONSTRAINT "_UserGuilds_A_fkey" FOREIGN KEY ("A") REFERENCES "Guild"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_UserGuilds" ADD CONSTRAINT "_UserGuilds_B_fkey" FOREIGN KEY ("B") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;
