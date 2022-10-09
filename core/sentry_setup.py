from raven import Client
from raven.versioning import fetch_git_sha
from raven.conf import setup_logging
from raven.handlers.logging import SentryHandler

from pathlib import Path


client = None


def init_sentry_logging():
    global client
    client = Client(
        dsn=("https://34acceccc58440b4bb3408b8fc3a778a@"
             "o1302274.ingest.sentry.io/6539445"),
        include_paths=(
            'core',
            'cogs.alias',
            'cogs.audio',
            'cogs.downloader',
            'cogs.economy',
            'cogs.general',
            'cogs.image',
            'cogs.streams',
            'cogs.trivia',
            'cogs.utils',
            'tests.core.test_sentry',
            'main',
            'launcher'
        ),
        release=fetch_git_sha(str(Path.cwd()))
    )

    handler = SentryHandler(client)
    setup_logging(
        handler,
        exclude=(
            "asyncio",
            "discord"
        )
    )