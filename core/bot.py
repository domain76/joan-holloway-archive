from discord.ext import commands
from collections import Counter
from core.utils.helpers import JsonGuildDB
from enum import Enum
import os


class Joan(commands.Bot):
    def __init__(self, cli_flags, **kwargs):
        self._shutdown_mode = ExitCodes.CRITICAL
        self.db = JsonGuildDB("core/data/settings.json",
                              autosave=True,
                              create_dirs=True)

        def prefix_manager(bot, message):
            global_prefix = self.db.get_global("prefix", [])
            if message.guild is None:
                return global_prefix
            server_prefix = self.db.get(message.guild, "prefix", [])
            return server_prefix if server_prefix else global_prefix

        # Priority: args passed > cli flags > db
        if "command_prefix" not in kwargs:
            if cli_flags.prefix:
                kwargs["command_prefix"] = lambda bot, message: cli_flags.prefix
            else:
                kwargs["command_prefix"] = None

        if kwargs["command_prefix"] is None:
            kwargs["command_prefix"] = prefix_manager

        self.counter = Counter()
        self.uptime = None
        super().__init__(**kwargs)

    async def is_owner(self, user, allow_coowners=True):
        if allow_coowners:
            if user.id in self.db.get_global("coowners", []):
                return True
        return await super().is_owner(user)

    async def send_cmd_help(self, ctx):
        if ctx.invoked_subcommand:
            pages = await self.formatter.format_help_for(ctx, ctx.invoked_subcommand)
            for page in pages:
                await ctx.send(page)
        else:
            pages = await self.formatter.format_help_for(ctx, ctx.command)
            for page in pages:
                await ctx.send(page)

    async def shutdown(self, *, restart=False):
        """Gracefully quits Joan with exit code 0

        If restart is True, the exit code will be 26 instead
        Upon receiving that exit code, the launcher restarts Joan"""
        if not restart:
            self._shutdown_mode = ExitCodes.SHUTDOWN
        else:
            self._shutdown_mode = ExitCodes.RESTART

        await self.logout()

    def list_packages(self):
        """Lists packages present in the cogs folder"""
        return os.listdir("cogs")

    async def save_packages_status(self):
        loaded = []
        for package in self.extensions:
            if package.startswith("cogs."):
                loaded.append(package)
        await self.db.set_global("packages", loaded)


class ExitCodes(Enum):
    CRITICAL = 1
    SHUTDOWN = 0
    RESTART = 26