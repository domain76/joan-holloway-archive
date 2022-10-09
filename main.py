from core.bot import Joan, ExitCodes
from core.global_checks import init_global_checks
from core.events import init_events
from core.json_flusher import init_flusher
from core.settings import parse_cli_flags
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


def init_loggers(cli_flags):
    dpy_logger = logging.getLogger("discord")
    dpy_logger.setLevel(logging.WARNING)
    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)
    dpy_logger.addHandler(console)

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

    return logger

if __name__ == '__main__':
    cli_flags = parse_cli_flags()
    log = init_loggers(cli_flags)
    init_flusher()
    description = "Joan Holloway - Alpha"
    joan = Joan(cli_flags, description=description, pm_help=None)
    init_global_checks(joan)
    init_events(joan)
    joan.load_extension('core')
    if cli_flags.dev:
        pass # load dev cog here?

    token = os.environ.get("JOAN_TOKEN", joan.db.get_global("token", None))

    if token is None:
        log.critical("No token to login with")
        sys.exit(1)

    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(joan.start(token, bot=not cli_flags.not_bot))
    except discord.LoginFailure:
        log.critical("This token doesn't seem to be valid. If it belongs to "
                     "a user account, remember that the --not-bot flag "
                     "must be used. For self-bot functionalities instead, "
                     "--self-bot")
    except KeyboardInterrupt:
        log.info("Keyboard interrupt detected. Quitting...")
        loop.run_until_complete(joan.logout())
        joan._shutdown_mode = ExitCodes.SHUTDOWN
    except Exception as e:
        log.critical("Fatal exception", exc_info=e)
        loop.run_until_complete(joan.logout())
    finally:
        sys.exit(joan._shutdown_mode.value)
