import discord
from discord.ext import commands
import os
import sys
import json
import asyncio

class Warning:
    """Bot commands for moderation."""
    def __init__(self, bot):
        self.bot = bot
        with open('saves/warns.json', 'r+') as f:
            self.warns = json.load(f)
        print('Addon "{}" loaded'.format(self.__class__.__name__))           
                
    @commands.has_permissions(kick_members=True)    
    @commands.command(pass_context=True)
    async def warn(self, ctx, member:discord.Member, *, reason="No reason given."):
        """Warn a member."""
        if not member:
            await ctx.send("That user could not be found.")
        else:
            owner = ctx.guild.owner
            if self.bot.staff_role in member.roles and not ctx.author == owner:
                return await ctx.send("You cannot warn a staff member!")
            try:
                self.warns[str(member.id)]
            except KeyError:
                self.warns[str(member.id)] = []
            self.warns[str(member.id)].append(reason)
            reply_msg = "Warned user {}#{}. This is warn {}.".format(member.name, member.discriminator, len(self.warns[str(member.id)]))
            private_message = "You have been warned by user {}#{}. The given reason was: `{}`\nThis is warn {}.".format(ctx.author.name, ctx.author.discriminator, reason, len(self.warns[str(member.id)]))
            if len(self.warns[str(member.id)]) >= 5:
                private_message += "\nYou were banned due to this warn.\nIf you feel that you did not deserve this ban, send a direct message to a staff member"
                try:
                    await member.send(private_message)
                except discord.Forbidden:
                    pass
                await self.bot.guild.ban(member, delete_message_days=0, reason="5+ warns, see logs for details.")
                reply_msg += " As a result of this warn, the user was banned."
                
            elif len(self.warns[str(member.id)]) == 4:
                private_message += "\nYou were kicked due to this warn."
                try:
                    await member.send(private_message)
                except discord.Forbidden:
                    pass
                await member.kick(reason="4 warns, see logs for details.")
                reply_msg += " As a result of this warn, the user was kicked. The next warn will automatically ban the user."
                
            elif len(self.warns[str(member.id)]) == 3:
                private_message += "\nYou were kicked due to this warn."
                try:
                    await member.send(private_message)
                except discord.Forbidden:
                    pass
                await member.kick(reason="3 warns, see logs for details.")
                reply_msg += " As a result of this warn, the user was kicked. The next warn will automatically kick the user."
                
            elif len(self.warns[str(member.id)]) == 2:
                private_message += "\nYour next warn will automatically kick you."
                try:
                    await member.send(private_message)
                except discord.Forbidden:
                    pass
                reply_msg += " The next warn will automatically kick the user."
                
            else:
                try:
                    await member.send(private_message)
                except:
                    pass
            await ctx.send(reply_msg)
            embed = discord.Embed(description="{0.name}#{0.discriminator} warned user <@{1.id}> | {1.name}#{1.discriminator}".format(ctx.author, member))
            embed.add_field(name="Reason given", value="• " + reason)
            await self.bot.log_channel.send(embed=embed)
            with open("saves/warns.json", "w+") as f:
                json.dump(self.warns, f, indent=4)
                
    @commands.command(pass_context=True)
    async def listwarns(self, ctx, *, member:discord.Member=None):
        """List a member's warns."""
        if member is None:
            member = ctx.author
        if not self.bot.staff_role in member.roles and not ctx.author == ctx.guild.owner and not ctx.message.author == member:
            await ctx.send("You don't have permission to use this command.")
        else:
            try:
                user_warns = self.warns[str(member.id)]
                if user_warns:
                    embed = discord.Embed(title="Warns for user {}#{}".format(member.name, member.discriminator), description="")
                    for warn in user_warns:
                        embed.description += "• {}\n".format(warn)
                    embed.set_footer(text="There are {} warns in total.".format(len(user_warns)))
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("That user has no warns!")
            except KeyError:
                await ctx.send("That user has no warns!")
                
    @commands.has_permissions(ban_members=True)    
    @commands.command(pass_context=True)
    async def clearwarns(self, ctx, *, member:discord.Member):
        """Clear a member's warns."""
        if not member:
            await ctx.send("That user could not be found.")
        else:            
            try:
                if self.warns[str(member.id)]:
                    self.warns[str(member.id)] = []
                    with open("saves/warns.json", "w+") as f:
                        json.dump(self.warns, f)
                    await ctx.send("Cleared the warns of user {}#{}.".format(member.name, member.discriminator))
                    embed = discord.Embed(description="{0.name}#{0.discriminator} cleared warns of user <@{1.id}> | {1.name}#{1.discriminator}".format(ctx.author, member))
                    await self.bot.log_channel.send(embed=embed)
                    try:
                        await member.send("All your warns have been cleared.")
                    except discord.errors.Forbidden:
                        pass
                else:
                    await ctx.send("That user has no warns!")
            except KeyError:
                await ctx.send("That user has no warns!")
                
    @commands.has_permissions(ban_members=True)    
    @commands.command(pass_context=True)
    async def unwarn(self, ctx, member:discord.Member, *, index=-1):
        """Take a specific warn off a user."""
        if not member:
            await ctx.send("That user could not be found.")
        else:            
            try:
                if self.warns[str(member.id)]:
                    if index > len(self.warns[str(member.id)]) or index == -1:
                        return await ctx.send("{} doesn't have a warn numbered `{}`!".format(member, index))
                    reason = self.warns[str(member.id)][index-1]
                    self.warns[str(member.id)].pop(index-1)
                    with open("saves/warns.json", "w+") as f:
                        json.dump(self.warns, f)
                    await ctx.send("Removed `{}` warn of user {}#{}.".format(reason, member.name, member.discriminator))
                    embed = discord.Embed(description="{} took a warn off of user <@{}> | {}\n{}".format(ctx.author, member.id, member, reason))
                    embed.add_field(name="Removed Warn", value="• " + reason)
                    await self.bot.log_channel.send(embed=embed)
                else:
                    await ctx.send("That user has no warns!")
            except KeyError:
                await ctx.send("That user has no warns!")
                
def setup(bot):
    bot.add_cog(Warning(bot))
