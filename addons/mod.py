#!/usr/bin/env python3

import discord
from discord.ext import commands
import os
import sys
import json
import asyncio

class Moderation:
    """Bot commands for moderation."""
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))
        
    def find_user(self, user, ctx):
        found_member = self.bot.guild.get_member(user)
        if not found_member:
            found_member = self.bot.guild.get_member_named(user)
        if not found_member:
            try:
                found_member = ctx.message.mentions[0]
            except IndexError:
                pass
        if not found_member:
            return None
        else:
            return found_member
    
    @commands.has_permissions(kick_members=True)    
    @commands.command(pass_context=True)
    async def kick(self, ctx, member, *, reason="No reason was given."):
        """Kick a member."""
        found_member = self.find_user(member, ctx)
        if found_member == ctx.message.author:
            return await ctx.send("You can't kick yourself, obviously")
        elif not found_member:
            await ctx.send("That user could not be found.")
        elif self.bot.staff_role in found_member.roles and ctx.author != ctx.guild.owner:
            return await ctx.send("That user is protected!")
        else:
            embed = discord.Embed(title="{} kicked".format(found_member), colour=discord.Color.orange())
            embed.description = "{}#{} was kicked by {} for:\n\n{}".format(found_member.name, found_member.discriminator, ctx.message.author, reason)
            await self.bot.log_channel.send(embed=embed)
            try:
                await found_member.send("You were kicked from SwitchHaxing for:\n\n`{}`".format(reason))
            except discord.Forbidden:
                pass # bot blocked or not accepting DMs
            await found_member.kick(reason=reason)
            await ctx.send("Successfully kicked user {0.name}#{0.discriminator}!".format(found_member))
     
    @commands.command(pass_context=True)
    async def ban(self, ctx, member, *, reason="No reason was given."):
        """Ban a member."""
        found_member = self.find_user(member, ctx)
        author_roles = ctx.message.author.roles[1:]
        if found_member == ctx.message.author:
            return await ctx.send("You can't ban yourself, obviously")
        elif found_member == ctx.guild.owner:
            return await ctx.send("{}#{} has been banned{}!".format(ctx.guild.owner.name, ctx.guild.owner.discriminator, " for reason: `{}`".format(reason) if reason != "No reason was given." else ""))
        elif not self.bot.staff_role in author_roles:
            return await ctx.send("You're not a mod!")
        elif self.bot.staff_role in found_member.roles and ctx.author != ctx.guild.owner:
            return await ctx.send("That member is protected!")
        elif not found_member:
            await ctx.send("That user could not be found.")
        else:
            embed = discord.Embed(title="{} banned".format(found_member), colour=discord.Color.red())
            embed.description = "{}#{} was banned by {} for:\n\n{}".format(found_member.name, found_member.discriminator, ctx.message.author, reason)
            embed.set_footer(text="Member ID = {}".format(found_member.id))
            await self.bot.log_channel.send(embed=embed)
            try:
                await found_member.send("You were banned from {} for:\n\n`{}`\n\nIf you believe this to be in error, please contact a staff member.".format(ctx.guild.name, reason))
            except:
                pass # bot blocked or not accepting DMs
            await found_member.ban(reason=reason)
            await ctx.send("Successfully banned user {0.name}#{0.discriminator}!".format(found_member))
            
    @commands.has_permissions(kick_members=True)
    @commands.command(aliases=['p'])
    async def purge(self, ctx, amount=0, *, reason=""):
        """Purge x amount of messages"""
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
        await ctx.s()
            
            
def setup(bot):
    bot.add_cog(Moderation(bot))
