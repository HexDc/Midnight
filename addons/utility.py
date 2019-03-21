#!/usr/bin/env python3

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
import sys
import os
import json
from datetime import datetime

serials = {
    "XAW1": (78, 79, 100),
    "XAW4": (11, 12, 13),
    "XAW7": (17, 18, 19),
    "XAJ4": (52, 53, 60),
    "XAJ7": (42, 43, 50)
}

class Utility:

    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))
            
    @commands.command()
    async def restart(self, ctx):
        """Restarts the bot, obviously"""
        if ctx.author != ctx.guild.owner and ctx.author != self.bot.creator:
            return await ctx.send("You can't use this!")
        await ctx.send("Restarting...")
        with open("restart.txt", "w+") as f:
            f.write(str(ctx.message.channel.id))
            f.close()
        sys.exit(0)
            
    @commands.command(hidden=True, aliases=['game', 'music', 'watch'])
    async def playing(self, ctx, *, presence=""):
        """Changes the bot's activity.'"""
        await ctx.message.delete()
        if ctx.author != ctx.guild.owner and ctx.author != self.bot.creator:
            return await ctx.send("You can't use this!")
        if ctx.invoked_with == "playing":
            return await ctx.send("You can use 'music', 'game', or 'watch' to choose an activity for the bot.")
        elif ctx.invoked_with == "game":
            key = "game"
            game = discord.Game(name=presence)
            await self.bot.change_presence(activity=game)
            await ctx.send("Changed game status to `{}`!".format(presence))
        elif ctx.invoked_with == "music":
            key = "music"
            music = discord.Activity(name=presence, type=discord.ActivityType.listening)
            await self.bot.change_presence(activity=music)
            await ctx.send("Changed music status to `{}`!".format(presence))
        elif ctx.invoked_with == "watch":
            key = "watch"
            show = discord.Activity(name=presence, type=discord.ActivityType.watching)
            await self.bot.change_presence(activity=show)
            await ctx.send("Changed video status to `{}`!".format(presence))
        with open('saves/bot_status.json', 'r') as f:
            status = json.load(f)
        status["status"] = key
        status["presence"] = presence
        with open('saves/bot_status.json', 'w') as f:
            json.dump(status, f, indent=4)
            
    @commands.command()
    async def about(self, ctx):
        """Information about the bot"""
        await ctx.send("This is a bot coded in python for use in the SwitchHaxing server, made primarily by {}#{}. You can view the source code here: <https://github.com/GriffinG1/Midnight>.".format(self.bot.creator.name, self.bot.creator.discriminator))
        
    @commands.command(aliases=['mc'])
    async def membercount(self, ctx):
        """Returns number of people in server"""
        members = 0
        for user in ctx.guild.members:
            if not user.bot:
                members += 1
        await ctx.send("There are {} members on this server!".format(members))
        
    async def role_change(ctx, role, user):
        if not role in user.roles:
            await user.add_roles(role)
        else:
            await user.remove_roles(role)
               
    @commands.command(aliases=['ui', 'user'])
    async def userinfo(self, ctx, user:discord.Member=None, depth=False):
        """Gets the userinfo for a given server member. If given no member, it will pull your own info. If you specify "True" after providing a member, you will see creation date, join date, and account age."""
        if not user:
            user = ctx.author
        embed = discord.Embed(title="User info for {}".format(user))
        embed.set_thumbnail(url=user.avatar_url)
        embed.add_field(name="Username", value="{}".format(user.name))
        embed.add_field(name="Status", value="{}".format(str(user.status).capitalize()))
        if user.nick:
            embed.add_field(name="Nickname", value="{}".format(user.nick))
        if user.bot:
            embed.add_field(name="Bot", value="{}".format(user.bot))
        if len(user.roles) > 1:
            embed.add_field(name="Highest Role", value="{}".format(user.top_role))
        embed.add_field(name="ID", value="{}".format(user.id))
        created_at_epoch = int((bin(user.id)[:-22])[2:], 2)
        if depth:
            embed.add_field(name="Created At", value="{} UTC".format(datetime.fromtimestamp((created_at_epoch+1420070400000) / 1000.0).strftime('%m-%d-%Y %H:%M:%S')))
            embed.add_field(name="Joined At", value="{} UTC".format(user.joined_at.strftime('%m-%d-%Y %H:%M:%S')))
            embed.add_field(name="Account Age", value="{} Days".format((datetime.now() - (datetime.fromtimestamp((created_at_epoch+1420070400000) / 1000.0))).days))
        await ctx.send(embed=embed)
        
    @commands.command(aliases=['si', 'server'])
    async def serverinfo(self, ctx):
        """Returns info about SwitchHaxing"""
        embed = discord.Embed(title="Server information")
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.add_field(name="Guild name", value="{}".format(ctx.guild.name))
        embed.add_field(name="ID", value="{}".format(ctx.guild.id))
        embed.add_field(name="Members", value="{}".format(ctx.guild.member_count))
        embed.add_field(name="Roles", value="{}".format(len(ctx.guild.roles)))
        embed.add_field(name="Created at", value="{}".format(ctx.guild.created_at))
        await ctx.send(embed=embed)
        
def setup(bot):
    bot.add_cog(Utility(bot))
