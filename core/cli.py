import argparse
import asyncio

from core.bot import Joan

def confirm(m=""):
    return input(m).lower().strip() in ("y", "yes")


def interactive_config(joan, token_set, prefix_set):
    loop = asyncio.get_event_loop()
    token = ""

    print("Joan Holloway | Configuration process\n")

    if not token_set:
        print("Please enter a valid token:")
        while not token:
            token = input("> ")
            if not len(token) >= 50:
                print("That doesn't look like a valid token.")
                token = ""
            if token:
                loop.run_until_complete(joan.db.set("token", token))

    if not prefix_set:
        prefix = ""
        print("\nPick a prefix. A prefix is what you type before a "
              "command. Example:\n"
              "!help\n^ The exclamation mark is the prefix in this case.\n"
              "Can be multiple characters. You will be able to change it "
              "later and add more of them.\nChoose your prefix:\n")
        while not prefix:
            prefix = input("Prefix> ")
            if len(prefix) > 10:
                print("Your prefix seems overly long. Are you sure it "
                      "is correct? (y/n)")
                if not confirm("> "):
                    prefix = ''
            if prefix:
                loop.run_until_complete(joan.db.set("prefix", [prefix]))

    ask_sentry(joan)

    return token



def ask_sentry(joan: Joan):
    loop = asyncio.get_event_loop()
    print("\nThank you for installing Joan Holloway alpha! The current version\n"
          " is not suited for production use and is aimed at testing\n"
          " the current and upcoming featureset, that's why we will\n"
          " also collect the fatal error logs to help us fix any new\n"
          " found issues in a timely manner. If you wish to opt in\n"
          " the process please type \"yes\":\n")
    if not confirm("> "):
        loop.run_until_complete(joan.db.set("enable_sentry", False))
    else:
        loop.run_until_complete(joan.db.set("enable_sentry", True))
        print("\nThank you for helping us with the development process!")


def parse_cli_flags():
    parser = argparse.ArgumentParser(description="Joan - Discord Bot")
    parser.add_argument("--owner", help="ID of the owner. Only who hosts "
                        "Joan should be owner, this has "
                        "security implications")
    parser.add_argument("--prefix", "-p", action="append",
                        help="Global prefix. Can be multiple")
    parser.add_argument("--no-prompt",
                        action="store_true",
                        help="Disables console inputs. Features requiring "
                        "console interaction could be disabled as a "
                        "result")
    parser.add_argument("--no-cogs",
                        action="store_true",
                        help="Starts Joan with no cogs loaded, only core")
    parser.add_argument("--self-bot",
                        action='store_true',
                        help="Specifies if Joan should log in as selfbot")
    parser.add_argument("--not-bot",
                        action='store_true',
                        help="Specifies if the token used belongs to a bot "
                        "account.")
    parser.add_argument("--dry-run",
                        action="store_true",
                        help="Makes Joan quit with code 0 just before the "
                        "login. This is useful for testing the boot "
                        "process.")
    parser.add_argument("--debug",
                        action="store_true",
                        help="Sets the loggers level as debug")
    parser.add_argument("--dev",
                       action="store_true",
                       help="Enables developer mode")

    args = parser.parse_args()

    if args.prefix:
        args.prefix = sorted(args.prefix, reverse=True)
    else:
        args.prefix = []

    return args