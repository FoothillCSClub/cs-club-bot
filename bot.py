"""
> ArchiveGlider
> Copyright (c) 2020 Xithrius
> GNU AGPL, Refer to LICENSE for more info
"""


import asyncio
import concurrent.futures
import json
import os
import sys
import traceback
import typing as t

import discord
import youtube_dl
from discord.ext import commands as comms
from hyper_status import Status

from utils import parallel_executor, path


class ArchiveGlider(comms.Bot):
    """ """

    def __init__(self, *args, **kwargs) -> None:
        """ """
        super().__init__(
            command_prefix='archive ', help_command=None,
            description='Automating tasks remotely from Discord'
        )

        with open(path('config', 'config.json'), 'r') as f:
            try:
                self.config = json.load(f)
            except IndexError:
                raise discord.errors.LoginFailure

        # Create asyncio loop
        self.loop = asyncio.get_event_loop()

        # Create executor for running sync functions asynchronously
        self.executor = concurrent.futures.ThreadPoolExecutor()

        self.load_extensions()

    def load_extensions(self):
        self.add_cog(Development(self))

    async def on_ready(self):
        """Updates the bot status when logged in successfully."""

        # url = 'https://youtu.be/DY8nqIfsQkU'
        await self.change_presence(activity=discord.Activity(
            type=discord.ActivityType.listening, name='Interstellar')
        )

        Status('Awaiting...', 'ok')


class Development(comms.Cog):

    def __init__(self, bot) -> None:
        self.bot = bot

    @parallel_executor
    def ytdl(self, url: str, file_path: t.Union[str, t.List[str]]) -> str:
        """ """
        if isinstance(file_path, list):
            file_path = (os.sep).join(map(str, file_path))

        data = {
            "format": "bestaudio/best",
            "outtmpl": f"{file_path}{os.sep}%(title)s.mp3",
            "restrictfilenames": True,
            "noplaylist": False,
            "nocheckcertificate": True,
            "ignoreerrors": True,
            "logtostderr": True,
            "quiet": True,
            "no_warnings": True,
            "default_search": "auto",
            "source_address": "0.0.0.0"
        }

        ytdl = youtube_dl.YoutubeDL(data)
        ytdl.extract_info(url, download=True)

    @comms.command()
    async def invite(self, ctx) -> None:
        """ """
        _id = self.bot.user.id
        url = f'https://discordapp.com/oauth2/authorize?client_id={_id}&scope=bot&permissions=379968'
        embed = discord.Embed(description=f'[`Invite`]({url})')
        await ctx.send(embed=embed)

    @comms.command(name='logout', aliases=['exit'])
    async def logout_command(self, ctx) -> None:
        """ """
        Status('Logging out...', 'warn')
        await self.bot.logout()

    @comms.command(aliases=['download', 'dl', 'ytdl'])
    @comms.is_owner()
    async def download_mp3(self, ctx, url: str) -> None:
        """ """
        msg = await ctx.send('Downloading files...')
        await self.ytdl(url, self.bot.config['mp3-dl-path'])
        await msg.add_reaction('\U00002705')


class Warnings(comms.Cog):
    """Warning the user about specific actions taken.

    Attributes:
        bot (:obj:`comms.Bot`): Represents a Discord bot.

    """

    def __init__(self, bot):
        """Creating important attributes for this class.

        Args:
            bot (:obj:`comms.Bot`): Represents a Discord bot.

        """
        self.bot = bot

    @comms.Cog.listener()
    async def on_command_error(self, ctx, error):
        """When the command has an error, this event is triggered.

        Args:
            ctx (comms.Context): Represents the context in which a command is being invoked under.
            error (comms.CommandError): The error that was raised

        """
        if hasattr(ctx.command, 'on_error'):
            return

        error = getattr(error, 'original', error)

        await ctx.message.add_reaction('\U0000274c')

        if isinstance(error, comms.DisabledCommand):
            return await ctx.send(f'`Command not available.`')

        elif isinstance(error, comms.CommandNotFound):
            return await ctx.send(f'`Command not found.`')

        elif isinstance(error, comms.UserInputError):
            return await ctx.send(f'`Command raised bad argument: {error}`')

        elif isinstance(error, comms.NotOwner):
            return await ctx.send('`You do not have enough permissions for this command.`')

        elif isinstance(error, comms.CommandOnCooldown):
            return await ctx.send(f'`{error}`')

        elif isinstance(error, comms.CheckFailure):
            if str(error).strip() == 'NSFW':
                return await ctx.send('`NSFW in SFW channels are not allowed.`')
            return await ctx.send(f'`You do not have enough permissions to run this command.`')

        elif isinstance(error, AssertionError):
            return await ctx.send(f'`Command failed: {error}`')

        else:
            print(f'Ignoring exception in command {ctx.command}:', file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
            await ctx.send(f'`Command has thrown error(s). See console for more info.`')


if __name__ == "__main__":

    try:
        bot = ArchiveGlider()
        bot.run(bot.config['discord'], bot=True, reconnect=True)

    except (discord.errors.HTTPException, discord.errors.LoginFailure):
        Status('Either an improper token has been passed, or it could not be found.', 'fail')

    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
