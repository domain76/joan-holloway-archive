from core.bot import Joan
from core.global_checks import init_global_checks
from core.events import init_events
from core.json_flusher import init_flusher
from core.settings import parse_cli_flags
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

if __name__ == '__main__':
    cli_flags = parse_cli_flags()
    init_loggers(cli_flags)
    init_flusher()
    description = "Joan Holloway - Alpha"
    joan = Joan(cli_flags, description=description, pm_help=None)
    init_global_checks(joan)
    init_events(joan)
    joan.load_extension('core')
    if cli_flags.dev:
        pass # load dev cog here?
    joan.run(os.environ['JOAN_TOKEN'], bot=not cli_flags.not_bot)