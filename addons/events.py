import discord
from discord.ext import commands
import asyncio
import git
from datetime import datetime

git = git.cmd.Git(".")

class Events:

    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))
                
    async def on_member_join(self, member):
        embed = discord.Embed(title="New member!", colour=discord.Color.green())
        embed.description = "{0.mention} | {0.name}#{0.discriminator} | {0.id}".format(member)
        embed.set_footer(text="Joined at {} Mountain Time".format(datetime.now().strftime('%H:%M:%S')))
        await self.bot.log_channel.send(embed=embed)
        
    async def on_member_remove(self, member):
        embed = discord.Embed(title="Member left.", colour=discord.Color.blue())
        embed.description = "{0.mention} | {0.name}#{0.discriminator} | {0.id}".format(member)
        embed.set_footer(text="Left at {} Mountain Time".format(datetime.now().strftime('%H:%M:%S')))
        await self.bot.log_channel.send(embed=embed)
                
                
    def embed_member_change(ctx, before, after, item):
        embed = discord.Embed(title="{} change for {}".format(item, before))
        if item == "Username":
            before_item = before.name
            after_item = after.name
        elif item == "Nickname":
            before_item = before.nick
            after_item = after.nick
        embed.description = "**Before**: {}\n**After**: {}\n**ID**: {}".format(before_item, after_item, before.id)
        embed.set_footer(text="Changed at {} Mountain Time".format(datetime.now().strftime('%H:%M:%S')))
        return embed
                
    async def on_member_update(self, before, after):
        # Nick and name change logging, add later
        if before.name != after.name:
            embed = self.embed_member_change(before, after, "Username")
            await self.bot.log_channel.send(embed=embed)
        elif before.nick != after.nick:
            embed = self.embed_member_change(before, after, "Nickname")
            await self.bot.log_channel.send(embed=embed)
        
    async def on_message(self, message):
        # auto ban on 15+ pings
        if len(message.mentions) > 15:
            embed = discord.Embed(description=message.content)
            await message.delete()
            await message.author.ban()
            await message.channel.send("{} was banned for attempting to spam user mentions.".format(message.author))
            await self.bot.log_channel.send("{} was banned for attempting to spam user mentions.".format(message.author))
        
        if isinstance(message.channel, discord.abc.GuildChannel) and 'git' in message.channel.name and message.author.name == 'GitHub':
            print('Pulling changes')
            git.pull()
            print('Changes pulled!')
            await self.bot.log_channel.send("Pulled latest changes!")
            
    async def on_message_delete(self, message):
        if isinstance(message.channel, discord.abc.GuildChannel) and message.author.id != self.bot.user.id and not message.author.bot:
            if message.channel not in self.bot.ignored_channels and not self.bot.message_purge:
                embed = discord.Embed(description=message.content)
                await self.bot.log_channel.send("Message by {} deleted in channel {}:".format(message.author, message.channel.mention), embed=embed)

        
def setup(bot):
    bot.add_cog(Events(bot))