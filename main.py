from core.bot import Joan, ExitCodes
from core.global_checks import init_global_checks
from core.events import init_events
from core.sentry_setup import init_sentry_logging
from core.cli import interactive_config, confirm, parse_cli_flags, ask_sentry
from core.core_commands import Core
from core.dev_commands import Dev
import asyncio
import discord
import logging.handlers
import logging
import os
import sys

#
# Joan Holloway - Discord Bot
#
# Made by domain76, Inc.
#

if discord.version_info.major < 1:
    print("You are not running the rewritten version of discord.py.\n\n"
          "In order to use Joan Holloway you MUST be running d.py version"
          " >= 1.0.0.")
    sys.exit(1)


def init_loggers(cli_flags):
    # d.py stuff
    dpy_logger = logging.getLogger("discord")
    dpy_logger.setLevel(logging.WARNING)
    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)
    dpy_logger.addHandler(console)

    # Joan stuff

    logger = logging.getLogger("joan")
    
    joan_format = logging.Formatter(
        '%(asctime)s %(levelname)s %(module)s %(funcName)s %(lineno)d: '
        '%(message)s',
        datefmt="[%d/%m/%Y %H:%M]")

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(joan_format)

    if cli_flags.debug:
        os.environ['PYTHONASYNCIODEBUG'] = '1'
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARNING)

    fhandler = logging.handlers.RotatingFileHandler(
        filename='joan.log', encoding='utf-8', mode='a',
        maxBytes=10**7, backupCount=5)
    fhandler.setFormatter(joan_format)

    logger.addHandler(fhandler)
    logger.addHandler(stdout_handler)

    # Sentry stuff
    sentry_logger = logging.getLogger("joan.sentry")
    sentry_logger.setLevel(logging.WARNING)

    return logger, sentry_logger


if __name__ == '__main__':
    cli_flags = parse_cli_flags()
    log, sentry_log = init_loggers(cli_flags)
    description = "Joan Holloway - Alpha"
    joan = Joan(cli_flags, description=description, pm_help=None)
    init_global_checks(joan)
    init_events(joan, cli_flags)

    joan.add_cog(Core())

    if cli_flags.dev:
        joan.add_cog(Dev())

    token = os.environ.get("JOAN_TOKEN", joan.db.token())
    prefix = cli_flags.prefix or joan.db.prefix()

    if token is None or not prefix:
        if cli_flags.no_prompt is False:
            new_token = interactive_config(joan, token_set=bool(token),
                                           prefix_set=bool(prefix))
            if new_token:
                token = new_token
        else:
            log.critical("Token and prefix must be set in order to login.")
            sys.exit(1)

    if joan.db.enable_sentry() is None:
        ask_sentry(joan)

    if joan.db.enable_sentry():
        init_sentry_logging(sentry_log)

    loop = asyncio.get_event_loop()
    cleanup_tasks = True

    try:
        loop.run_until_complete(joan.start(token, bot=not cli_flags.not_bot))
    except discord.LoginFailure:
        cleanup_tasks = False # No login happened, no need for this
        log.critical("This token doesn't seem to be valid. If it belongs to "
                     "a user account, remember that the --not-bot flag "
                     "must be used. For self-bot functionalities instead, "
                     "--self-bot")
        db_token = joan.db.token()
        if db_token and not cli_flags.no_prompt:
            print("\nDO you want to reset the token? (y/n)")
            if confirm("> "):
                loop.run_until_complete(joan.db.set("token", ""))
                print("Token has been reset.")
    except KeyboardInterrupt:
        log.info("Keyboard interrupt detected. Quitting...")
        loop.run_until_complete(joan.logout())
        joan._shutdown_mode = ExitCodes.SHUTDOWN
    except Exception as e:
        log.critical("Fatal exception", exc_info=e)
        sentry_log.critical("Fatal Exception", exc_info=e)
        loop.run_until_complete(joan.logout())
    finally:
        if cleanup_tasks:
            pending = asyncio.Task.all_tasks(loop=joan.loop)
            gathered = asyncio.gather(*pending, loop=joan.loop)
            gathered.cancel()
            joan.loop.run_until_complete(gathered)
            gathered.exception()

        sys.exit(joan._shutdown_mode.value)