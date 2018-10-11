#!/usr/bin/env python3

import discord
from discord.ext import commands
import os
import sys
import json
import asyncio
import json
from datetime import datetime

class Moderation:
    """Bot commands for moderation."""
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))
    
    @commands.has_permissions(kick_members=True)    
    @commands.command(pass_context=True)
    async def kick(self, ctx, member:discord.Member, *, reason="No reason was given."):
        """Kick a member."""
        if member == ctx.message.author:
            return await ctx.send("You can't kick yourself, obviously")
        elif not member:
            await ctx.send("That user could not be found.")
        elif self.bot.staff_role in member.roles and ctx.author != ctx.guild.owner:
            return await ctx.send("That user is protected!")
        else:
            embed = discord.Embed(title="{} kicked".format(member))
            embed.description = "{}#{} was kicked by {} for:\n\n{}".format(member.name, member.discriminator, ctx.message.author, reason)
            embed.set_footer(text="Member ID = {}".format(member.id))
            await self.bot.log_channel.send(embed=embed)
            try:
                await member.send("You were kicked from SwitchHaxing for:\n\n`{}`\n\nThis has added a single warn to you as well.".format(reason))
            except discord.Forbidden:
                pass # bot blocked or not accepting DMs
            await member.kick(reason=reason)
            with open('saves/warns.json', 'r+') as f:
                warns = json.load(f)
            try:
                warns[str(member.id)]
            except KeyError:
                warns[str(member.id)] = []
            warns[str(member.id)].append(reason)
            with open("saves/warns.json", "w+") as f:
                json.dump(warns, f, indent=4)
            await ctx.send("Successfully kicked user {}#{}!".format(member.name, member.discriminator))
     
    @commands.command(pass_context=True)
    async def ban(self, ctx, member:discord.Member, *, reason="No reason was given."):
        """Ban a member."""
        author_roles = ctx.message.author.roles[1:]
        if member == ctx.message.author:
            return await ctx.send("You can't ban yourself, obviously")
        elif member == ctx.guild.owner:
            return await ctx.send("{}#{} has been banned{}!".format(ctx.guild.owner.name, ctx.guild.owner.discriminator, " for reason: `{}`".format(reason) if reason != "No reason was given." else ""))
        elif not self.bot.staff_role in author_roles:
            return await ctx.send("You're not a mod!")
        elif self.bot.staff_role in member.roles and ctx.author != ctx.guild.owner:
            return await ctx.send("That member is protected!")
        elif not member:
            await ctx.send("That user could not be found.")
        else:
            embed = discord.Embed(title="{} banned".format(member))
            embed.description = "{}#{} was banned by {} for:\n\n{}".format(member.name, member.discriminator, ctx.message.author, reason)
            embed.set_footer(text="Member ID = {}".format(member.id))
            await self.bot.log_channel.send(embed=embed)
            try:
                await member.send("You were banned from {} for:\n\n`{}`\n\nIf you believe this to be in error, please contact a staff member.".format(ctx.guild.name, reason))
            except:
                pass # bot blocked or not accepting DMs
            await member.ban(reason=reason)
            await ctx.send("Successfully banned user {}#{}!".format(member.name, member.discriminator))
            
    @commands.command()
    async def hackban(self, ctx, member, *, reason="No reason was given."):
        """Bans a user by ID. Only use on non-guild members. Restricted to guild owner and bot creator"""
        if ctx.message.author != self.bot.creator and ctx.message.author != ctx.guild.owner:
            return await ctx.send("You don't have permission to use this!")
        id = member.replace('<', '').replace('>', '').replace('@', '').replace('!', '')
        if not id.isdigit():
            return await ctx.send("That is not a user ID.")
        try:
            user = discord.Object(id=id)
        except:
            return await ctx.send("Converting to object failed")
        await self.bot.guild.ban(user)
        await ctx.send("ID `{}` banned.".format(id))
        embed = discord.Embed(title="ID {} banned".format(id))
        embed.description = "User ID of {} was banned by {} for:\n\n{}".format(id, ctx.message.author, reason)
        embed.set_footer(text="ID banned at {} UTC±0".format(datetime.now().strftime('%H:%M:%S')))
        await self.bot.log_channel.send(embed=embed)
            
    @commands.has_permissions(ban_members=True)    
    @commands.command()
    async def mute(self, ctx, member:discord.Member, *, reason=""):
        """Mute a member."""
        if member == ctx.message.author:
            return await ctx.send("Why are you trying to mute yourself?")
        elif not member:
            await ctx.send("That user could not be found.")
        elif self.bot.staff_role in member.roles and ctx.author != ctx.guild.owner:
            return await ctx.send("You can't mute a fellow staff member!")
        elif self.bot.mute_role in member.roles:
            return await ctx.send("That user is already muted!")
        else:
            await member.add_roles(self.bot.mute_role)
            await ctx.send("Successfully muted user {}#{}!".format(member.name, member.discriminator))
            embed = discord.Embed(title="{} muted".format(member))
            embed.description = "{}#{} muted user {}#{} for `{}`".format(ctx.message.author.name, ctx.message.author.discriminator, member.name, member.discriminator, reason if reason != "" else "No reason was given")
            embed.set_footer(text="Member ID = {}".format(member.id))
            await self.bot.log_channel.send(embed=embed)
            try:
                await member.send("You have been muted on SwitchHaxing.\n{}\nIf you feel this mute was unwarranted, dm a staff member.".format(reason))
            except discord.errors.Forbidden:
                pass # Bot blocked
            
    @commands.has_permissions(ban_members=True)    
    @commands.command()
    async def unmute(self, ctx, *, member:discord.Member):
        """Unmute a member."""
        if member == ctx.message.author:
            return await ctx.send("How did you manage to mute yourself...")
        elif not member:
            return await ctx.send("That user could not be found.")
        elif not self.bot.mute_role in member.roles:
            return await ctx.send("That user isn't muted!")
        else:
            await member.remove_roles(self.bot.mute_role)
            embed = discord.Embed(title = "{} unmuted".format(member))
            embed.description = "{}#{} unmuted user {}#{}".format(ctx.message.author.name, ctx.message.author.discriminator, member.name, member.discriminator)
            embed.set_footer(text="Member ID = {}".format(member.id))
            await self.bot.log_channel.send(embed=embed)
            await ctx.send("Successfully unmuted user {}#{}!".format(member.name, member.discriminator))
            
    @commands.has_permissions(kick_members=True)
    @commands.command(aliases=['p'])
    async def purge(self, ctx, amount, *, reason=""):
        """Purge x amount of messages"""
        if not isinstance(amount, int):
            return await ctx.send("Error, `{}` is not an integer!".format(amount), delete_after=10)
        else:
            amount = 0
        await ctx.message.delete()
        asyncio.sleep(3)
        if amount > 0:
            self.bot.message_purge = True
            await ctx.channel.purge(limit=amount)
            asyncio.sleep(4)
            self.bot.message_purge = False
            message = "{} purged {} messages in {}".format(ctx.author, amount, ctx.channel.mention)
            if reason:
                message += " for `{}`".format(reason)
            await self.bot.log_channel.send(message)
        else:
            await ctx.send("Why would you wanna purge no messages?", delete_after=10)
        
    @commands.command(aliases=['ge'], hidden=True)
    async def guaranteed_error(self, ctx):
        if not ctx.author == self.bot.creator:
            await ctx.message.delete()
            await ctx.author.send("This command is restricted to the bot creator.")
        await ctx.s()
        
    @commands.command(aliases=['setfw'])
    async def setfirmwareinfo(self, ctx, version="", *, content=""):
        """Allows updating of firmware info"""
        if not content or not version:
            return await ctx.send("Error, missing parameters.")
        elif not self.bot.staff_role in ctx.author.roles and not ctx.author == self.bot.creator:
            return await ctx.send("You don't have permission to use this.")
        with open('saves/fwinfo.json', 'r') as f:
            firmware = json.load(f)
        firmware[version] = content
        with open('saves/fwinfo.json', 'w') as f:
            json.dump(firmware, f, indent=4)
        await ctx.send("Updated version `{}`".format(version))
            
def setup(bot):
    bot.add_cog(Moderation(bot))
