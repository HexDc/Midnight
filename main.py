# import dependencies
import os
from discord.ext import commands
import discord
import datetime
import json, asyncio
import copy
import configparser
import traceback
import sys
import os
import re
import ast
import shutil
from pathlib import Path

import config

# sets working directory to bot's folder
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)

token = config.token
prefix = config.prefix
description = config.description

bot = commands.Bot(command_prefix=prefix, description=description)

bot.dir_path = os.path.dirname(os.path.realpath(__file__))
bot.command_list = []

def get_command_list():
    bot.command_list = []
    for command in bot.commands:
        bot.command_list.append(command.name)
        bot.command_list.extend(command.aliases)
        
bot.get_command_list = get_command_list

@bot.check # taken and modified from https://discordpy.readthedocs.io/en/rewrite/ext/commands/commands.html#global-checks
async def globally_block_dms(ctx):
    if ctx.guild is None:
        raise discord.ext.commands.NoPrivateMessage('test')
        return False
    return True

# mostly taken from https://github.com/Rapptz/discord.py/blob/async/discord/ext/commands/bot.py
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        pass  # ...don't need to know if commands don't exist
    elif isinstance(error, discord.ext.commands.NoPrivateMessage):
        await ctx.send("You cannot use this command in DMs!")
    elif isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        formatter = commands.formatter.HelpFormatter()
        await ctx.send("You are missing required arguments.\n{}".format(formatter.format_help_for(ctx, ctx.command)[0]))
    elif isinstance(error, discord.ext.commands.errors.CheckFailure):
        await ctx.send("You don't have permission to use this command.")
    else:
        if ctx.command:
            await ctx.send("An error occurred while processing the `{}` command.".format(ctx.command.name))
        print('Ignoring exception in command {0.command} in {0.message.channel}'.format(ctx))
        tb = traceback.format_exception(type(error), error, error.__traceback__)
        error_trace = "".join(tb)
        print(error_trace)
        if bot.log_channel:
            embed = discord.Embed(description=error_trace)
            await bot.log_channel.send("An error occurred while processing the `{}` command in channel `{}`.".format(ctx.command.name, ctx.message.channel), embed=embed)

@bot.event
async def on_error(event_method, *args, **kwargs):
    if isinstance(args[0], commands.errors.CommandNotFound):
        return
    print("Ignoring exception in {}".format(event_method))
    tb = traceback.format_exc()
    error_trace = "".join(tb)
    print(error_trace)
    if bot.log_channel:
        embed = discord.Embed(description=error_trace)
        await bot.log_channel.send("An error occurred while processing `{}`.".format(event_method), embed=embed)


@bot.event
async def on_ready():
    for guild in bot.guilds:
        try:
            bot.guild = guild
                
            bot.creator = discord.utils.get(guild.members, id=177939404243992578)
            
            bot.log_channel = discord.utils.get(guild.channels, id=486994270620876830)
            bot.ignored_channels = {bot.log_channel}
            for id in config.ignored_chans:
                bot.ignored_channels.add(discord.utils.get(guild.channels, id=id))
                
            bot.spoiler_role = discord.utils.get(guild.roles, id=409749833176580097)
            bot.direct_role = discord.utils.get(guild.roles, id=421417111169138712)
            bot.staff_role = discord.utils.get(guild.roles, id=349851767078649859)
            bot.mute_role = discord.utils.get(guild.roles, id=385493119233163265)
                
            bot.message_purge = False
            
            get_command_list()
                
                
            with open('saves/bot_status.json', 'r') as f:
                status = json.load(f)
                
            if status["status"] == "game":
                await bot.change_presence(activity=discord.Game(name=status["presence"]))
            elif status["status"] == "music":
                await bot.change_presence(activity=discord.Activity(name=status["presence"], type=discord.ActivityType.listening))
            elif status["status"] == "watch":
                await bot.change_presence(activity=discord.Activity(name=status["presence"], type=discord.ActivityType.watching))
                
            if not Path("saves/warns.json").exists():
                print("saves/warns.json doesn't exist. Creating from sample file")
                try:
                    shutil.copy("saves/warns.json.sample", "saves/warns.json")
                    bot.load_extension('addons.warn')
                except:
                    print("saves/warns.json.sample doesn't exist. Please download from repo.")
            if not Path("saves/fwinfo.json").exists():
                print("saves/fwinfo.json doesn't exist. Creating from sample file")
                try:
                    shutil.copy("saves/fwinfo.json.sample", "saves/fwinfo.json")
                except:
                    print("saves/fwinfo.json.sample doesn't exist. Please download from repo.")
            if not Path("saves/bot_status.json").exists():
                print("saves/bot_status.json doesn't exist. Creating from sample file")
                try:
                    shutil.copy("saves/bot_status.json.sample", "saves/bot_status.json")
                except:
                    print("saves/bot_status.json.sample doesn't exist. Please download from repo.")
            
            print("Initialized on {}.".format(guild.name))
        except Exception as e:
            print("Failed to initialize on {}".format(guild.name))
            print("\t{}".format(e))

    
# loads extensions
addons = [
    'addons.events',
    'addons.utility',
    'addons.mod',
    'addons.warn',
    'addons.misc',
]

failed_addons = []

for extension in addons:
    try:
        bot.load_extension(extension)
    except Exception as e:
        print('{} failed to load.\n{}: {}'.format(extension, type(e).__name__, e))
        failed_addons.append([extension, type(e).__name__, e])
if not failed_addons:
    print('All addons loaded!')
        
@bot.command()
async def reload(ctx):
    """Reloads an addon."""
    if ctx.author != ctx.guild.owner and ctx.author != bot.creator:
        return await ctx.send("You can't use this!")
    errors = ""
    for addon in os.listdir("addons"):
        if ".py" in addon:
            addon = addon.replace('.py', '')
            try:
                bot.unload_extension("addons.{}".format(addon))
                bot.load_extension("addons.{}".format(addon))
            except Exception as e:
                errors += 'Failed to load addon: `{}.py` due to `{}: {}`\n'.format(addon, type(e).__name__, e)
    if not errors:
        bot.get_command_list()
        await ctx.send(':white_check_mark: Extensions reloaded.')
    else:
        await ctx.send(errors)
        
@bot.command(hidden=True)
async def load(ctx, *, module):
    """Loads an addon"""
    if ctx.author != ctx.guild.owner and ctx.author != bot.creator:
        return await ctx.send("You can't use this!")
    try:
        bot.load_extension("addons.{}".format(module))
    except Exception as e:
        await ctx.send(':anger: Failed!\n```\n{}: {}\n```'.format(type(e).__name__, e))
    else:
        bot.get_command_list()
        await ctx.send(':white_check_mark: Extension loaded.')
        
@bot.command(hidden=True)
async def botedit(ctx, *, name=""):
    """Edits the bot profile. Takes name only, at the moment. Bot owner only"""
    await ctx.message.delete()
    if ctx.author != bot.creator:
        return
    if not name:
        name = bot.user.name
    return await bot.user.edit(username=name)
    
async def pingfunc(ctx): # taken from https://github.com/appu1232/Discord-Selfbot/blob/873a2500d2c518e0d25ca5a6f67828de60fbda99/cogs/misc.py#L626
    msgtime = ctx.message.created_at.now()
    await (await bot.ws.ping())
    now = datetime.datetime.now()
    return now - msgtime

@bot.command(hidden=True) 
async def ping(ctx):
    """Get response time."""
    ping = await pingfunc(ctx)
    await ctx.send('Response Time: %s ms' % str(ping.microseconds / 1000.0))
    
@bot.command(hidden=True)
async def avgping(ctx, count=5):
    if count > 100:
        return await ctx.send("That's too many samples! Limit is 100")
    elif count <= 0:
        return await ctx.send("You can't take the average of a non positive number of samples!")
    ping_total = datetime.timedelta()
    for x in range(count):
        ping_total += await pingfunc(ctx)
    average_ping = ping_total / count
    await ctx.send('Average Response Time: %s ms' % str(average_ping.microseconds / 1000.0))
    
    
# Execute
print('Bot directory: ', dir_path)
bot.run(token)
