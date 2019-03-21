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

class Miscellaneous:

    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))
       
    @commands.command()
    async def say(self, ctx, *, str=""):
        """Says a message through the bot"""
        await ctx.message.delete()
        str = str.replace('@everyone', '`@everyone`').replace('@here', '`@here`')
        await ctx.send("{}".format(str))
        
def setup(bot):
    bot.add_cog(Miscellaneous(bot))
