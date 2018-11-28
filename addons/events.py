    # Midnight is a bot written in discord.py originally for use on the SwitchHaxing Discord Server
    # Copyright (C) 2018  GriffinG1

    # This program is free software: you can redistribute it and/or modify
    # it under the terms of the GNU Affero General Public License as published
    # by the Free Software Foundation, either version 3 of the License, or
    # (at your option) any later version.

    # This program is distributed in the hope that it will be useful,
    # but WITHOUT ANY WARRANTY; without even the implied warranty of
    # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    # GNU Affero General Public License for more details.

    # You should have received a copy of the GNU Affero General Public License
    # along with this program.  If not, see <https://www.gnu.org/licenses/>.
    
    # GriffinG1 can be contacted via GitHub (https://github.com/GriffinG1) or on Discord (A Ghost in the Dust#5250)

import discord
from discord.ext import commands
import asyncio
#import git
from datetime import datetime, timedelta

# git = git.cmd.Git(".")

piracy_tools = [
    #filtered items go here
]

class Events:

    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))
                
    async def on_member_join(self, member):
        rejoin = False
        with open('saves/mutes.json', 'r') as f:
                mutes = json.load(f)
        if mutes[str(member.id)][0] == "M":
            member.add_roles(self.bot.mute_role)
            await member.send_message("You were remuted, as you left while muted.")
        embed = discord.Embed(title="New member!", colour=discord.Color.green())
        embed.description = "{0.mention} | {0.name}#{0.discriminator} | {0.id}".format(member)
        if rejoin == True:
            embed.description += "\nUser has rejoined to attempt to remove a mute."
        account_creation_date = (datetime.fromtimestamp((int((bin(member.id)[:-22])[2:], 2)+1420070400000) / 1000.0))
        if (datetime.now() - account_creation_date).days < 7:
            embed.add_field(name="New account!", value="Created At: {}\nAge: {} Days".format(member.created_at.strftime('%m-%d-%Y %H:%M:%S'), (datetime.now()-account_creation_date).days))
        embed.set_footer(text="Joined at {} UTC±0".format(datetime.now().strftime('%H:%M:%S')))
        await self.bot.log_channel.send(embed=embed)
        if (self.bot.guild.member_count-1) % 100 == 0: #Only one bot on server currently
            await self.bot.log_channel.send("We've reached a milestone! There are {} members on this server!".format(self.bot.guild.member_count-1))
        
    async def on_member_remove(self, member):
        embed = discord.Embed(title="Member left.", colour=discord.Color.blue())
        embed.description = "{0.mention} | {0.name}#{0.discriminator} | {0.id}".format(member)
        embed.set_footer(text="Left at {} UTC±0".format(datetime.now().strftime('%H:%M:%S')))
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
        embed.set_footer(text="Changed at {} UTC±0".format(datetime.now().strftime('%H:%M:%S')))
        return embed
                
    async def on_member_update(self, before, after):
        if before.name != after.name:
            embed = self.embed_member_change(before, after, "Username")
            await self.bot.log_channel.send(embed=embed)
        elif before.nick != after.nick:
            embed = self.embed_member_change(before, after, "Nickname")
            await self.bot.log_channel.send(embed=embed)
        elif before.roles != after.roles:
            embed = discord.Embed()
            if len(before.roles) < len(after.roles):
                role = list(set(after.roles)-set(before.roles))
                embed.title = "Role added to {}".format(before)
                embed.set_footer(text="Role added at {} UTC±0".format(datetime.now().strftime('%H:%M:%S')))
            else:
                role = list(set(before.roles)-set(after.roles))
                embed.title = "Role removed from {}".format(before)
                embed.set_footer(text="Role removed at {} UTC±0".format(datetime.now().strftime('%H:%M:%S')))
            embed.description = "{}".format(role[0])
            await self.bot.log_channel.send(embed=embed)
            
    async def check_for_piracy(self, ctx, message):
        str = message.content.lower().replace(',', '').replace('`', '').replace('.', '').lower()
        for banned_word in piracy_tools:
            if banned_word in str:
                await message.delete()
                sent_message = " you mentioned a piracy tool. Please read the rules in <#349714057449832448>, and watch what you send!"
                try:
                    await message.author.send("Your message in {} was deleted as".format(message.channel.mention) + sent_message + "\n\nBanned word: `{}`\n\n Your message: `{}`".format(banned_word, message.content))
                except discord.Forbidden:
                    await message.channel.send("{}".format(message.author.mention) + sent_message)
                embed = discord.Embed(title="Piracy tool mentioned!")
                embed.description = "{} mentioned the piracy tool `{}` in {}.".format(message.author.mention, banned_word, message.channel.mention)
                embed.set_footer(text="Tool mentioned at {} UTC±0".format(datetime.now().strftime('%H:%M:%S')))
                await self.bot.log_channel.send(embed=embed)
        
    async def on_message(self, message):
        # auto ban on 15+ pings
        if len(message.mentions) > 15:
            embed = discord.Embed(description=message.content)
            await message.delete()
            await message.author.ban()
            await message.channel.send("{} was banned for attempting to spam user mentions.".format(message.author))
            await self.bot.log_channel.send("{} was banned for attempting to spam user mentions.".format(message.author))
            
        # filter piracy_tools
        if not message.author == self.bot.creator and not message.author.bot and not self.bot.staff_role in message.author.roles:
            try:
                await self.check_for_piracy(self, message)
            except discord.NotFound:
                print("Had an issue deleting the message. But it did delete. No clue why.")
            
        
        # if isinstance(message.channel, discord.abc.GuildChannel) and 'git' in message.channel.name and message.author.name == 'GitHub':
            # print('Pulling changes')
            # git.pull()
            # print('Changes pulled!')
            # await self.bot.log_channel.send("Pulled latest changes!")
                
    async def on_message_edit(self, before, after):
        if before.pinned != after.pinned:
            if after.pinned is True:
                pin_state = "Pinned"
            else:
                pin_state = "Unpinned"
            embed = discord.Embed(description=after.content)
            embed.set_footer(text="{} at {} UTC±0".format(pin_state, datetime.now().strftime('%H:%M:%S')))
            await self.bot.log_channel.send("Message by {} {} in {}".format(after.author, pin_state.lower(), after.channel.mention), embed=embed)
        elif before.content != after.content:
            embed = discord.Embed()
            embed.description = "**Before**: {}\n**After**: {}".format(before.content, after.content)
            embed.set_footer(text="Edited at {} UTC±0".format(datetime.now().strftime('%H:%M:%S')))
            await self.bot.log_channel.send("Message by {} edited in {}".format(after.author, after.channel.mention), embed=embed)
        # filter piracy tools
        if not after.author == self.bot.creator and not after.author.bot and not self.bot.staff_role in after.author.roles:
            try:
                await self.check_for_piracy(self, after)
            except discord.NotFound:
                print("Had an issue deleting the edited message. But it did delete. No clue why.")

    async def on_message_delete(self, message):
        if isinstance(message.channel, discord.abc.GuildChannel) and message.author.id != self.bot.user.id and not message.author.bot and not message.content.startswith(tuple(self.bot.command_list), 1):
            if message.channel not in self.bot.ignored_channels and not self.bot.message_purge:
                if not message.content: # Message is standalone image. Temporary until deleted image logging functions
                    return
                embed = discord.Embed(description=message.content)
                embed.set_footer(text="Deleted at {} UTC±0".format(datetime.now().strftime('%H:%M:%S')))
                await self.bot.log_channel.send("Message by {} deleted in channel {}:".format(message.author, message.channel.mention), embed=embed)
        
def setup(bot):
    bot.add_cog(Events(bot))
