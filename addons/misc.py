#!/usr/bin/env python3

import discord
from discord.ext import commands
import sys
import os

class Miscellaneous:

    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))
       
    @commands.command()
    async def bean(self, ctx, *, str=""):
        """Beans a user"""
        if not str:
            str = ctx.author
        else:
            str = str.replace('@everyone', '`@everyone`').replace('@here', '`@here`')
        await ctx.send("{} is now <:banB:423155991706730499><:banE:423155991798874121><:banA:423155991664787456><:banN:423155991497146380><:banE:423155991798874121><:banD:423155991677501440>".format(str))
        
    @commands.command()
    async def say(self, ctx, *, str=""):
        """Says a message through the bot"""
        await ctx.message.delete()
        str = str.replace('@everyone', '`@everyone`').replace('@here', '`@here`')
        await ctx.send("{}".format(str))
        
def setup(bot):
    bot.add_cog(Miscellaneous(bot))