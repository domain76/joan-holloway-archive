from discord.ext import commands
from core.utils.chat_formatting import escape, italics, pagify
from random import randint, choice
from enum import Enum
from urllib.parse import quote_plus
import discord
import datetime
import time
import aiohttp


class RPS(Enum):
    rock = "\N{MOYAI}"
    paper = "\N{PAGE FACING UP}"
    scissors = "\N{BLACK SCISSORS}"


class RPSParser:
    def __init__(self, argument):
        argument = argument.lower()
        if argument == "rock":
            self.choice = RPS.rock
        elif argument == "paper":
            self.choice = RPS.paper
        elif argument == "scissors":
            self.choice = RPS.scissors
        else:
            raise


class General(commands.Cog):
    """General commands."""

    def __init__(self):
        self.stopwatches = {}
        self.ball = [
            "As I see it, yes", "It is certain", "It is decidedly so",
            "Most likely", "Outlook good", "Signs point to yes",
            "Without a doubt", "Yes", "Yes - definitely", "You may rely on it",
            "Reply hazy, try again", "Ask again later",
            "Better not tell you now", "Cannot predict now",
            "Concentrate and ask again", "Don't count on it", "My reply is no",
            "My sources say no", "Outlook not so good", "Very doubtful"
        ]

    @commands.command(hidden=True)
    async def ping(self, ctx):
        """Pong."""
        await ctx.send("Pong.")

    @commands.command()
    async def choose(self, ctx, *choices):
        """Chooses between multiple choices.

        To denote multiple choices, you should use double quotes.
        """
        choices = [escape(c, mass_mentions=True) for c in choices]
        if len(choices) < 2:
            await ctx.send('Not enough choices to pick from.')
        else:
            await ctx.send(choice(choices))

    @commands.command()
    async def roll(self, ctx, number: int = 100):
        """Rolls random number (between 1 and user choice)

        Defaults to 100.
        """
        author = ctx.author
        if number > 1:
            n = randint(1, number)
            await ctx.send(
                "{} :game_die: {} :game_die:".format(author.mention, n)
            )
        else:
            await ctx.send("{} maybe choose a number higher than 1? ;P".format(author.mention))

    @commands.command()
    async def flip(self, ctx, user: discord.Member = None):
        """Flips a coin... or a user.

        Defaults to coin.
        """
        if user != None:
            msg = ""
            if user.id == ctx.bot.user.id:
                user = ctx.author
                msg = "Nice try! You think this is funny?" + \
                      "How about *this* instead:\n\n"
            char = "abcdefghijklmnopqrstuvwxyz"
            tran = "ɐqɔpǝɟƃɥᴉɾʞlɯuodbɹsʇnʌʍxʎz"
            table = str.maketrans(char, tran)
            name = user.display_name.translate(table)
            char = char.upper()
            tran = "∀qƆpƎℲפHIſʞ˥WNOԀQᴚS┴∩ΛMX⅄Z"
            table = str.maketrans(char, tran)
            name = name.translate(table)
            await ctx.send(msg + "(╯°□°）╯︵ " + name[::-1])
        else:
            await ctx.send(
                "*flips a coin and... " + choice(["HEADS!*", "TAILS!*"])
            )

    @commands.command()
    async def rps(self, ctx, your_choice: RPSParser):
        """Play rock paper scissors"""
        author = ctx.author
        player_choice = your_choice.choice
        joan_choice = choice((RPS.rock, RPS.paper, RPS.scissors))
        cond = {
            (RPS.rock, RPS.paper): False,
            (RPS.rock, RPS.scissors): True,
            (RPS.paper, RPS.rock): True,
            (RPS.paper, RPS.scissors): False,
            (RPS.scissors, RPS.rock): False,
            (RPS.scissors, RPS.paper): True
        }

        if joan_choice == player_choice:
            outcome = None  # Tie
        else:
            outcome = cond[(player_choice, joan_choice)]

        if outcome is True:
            await ctx.send("{} You win {}!".format(
                joan_choice.value, author.mention
            ))
        elif outcome is False:
            await ctx.send("{} You lose {}!".format(
                joan_choice.value, author.mention
            ))
        else:
            await ctx.send("{} We're square {}!".format(
                joan_choice.value, author.mention
            ))

    @commands.command(name="8", aliases=["8ball"])
    async def _8ball(self, ctx, *, question: str):
        """Ask 8 ball a question

        Question must end with a question mark.
        """
        if question.endswith("?") and question != "?":
            await ctx.send("`" + choice(self.ball) + "`")
        else:
            await ctx.send("That doesn't look like a question.")

    @commands.command(aliases=["sw"])
    async def stopwatch(self, ctx):
        """Starts/stops stopwatch"""
        author = ctx.author
        if not author.id in self.stopwatches:
            self.stopwatches[author.id] = int(time.perf_counter())
            await ctx.send(author.mention + " Stopwatch started!")
        else:
            tmp = abs(self.stopwatches[author.id] - int(time.perf_counter()))
            tmp = str(datetime.timedelta(seconds=tmp))
            await ctx.send(author.mention + " Stopwatch stopped! Time: **" + tmp + "**")
            self.stopwatches.pop(author.id, None)

    @commands.command()
    async def lmgtfy(self, ctx, *, search_terms: str):
        """Creates a lmgtfy link"""
        search_terms = escape(search_terms.replace(" ", "+"), mass_mentions=True)
        await ctx.send("https://lmgtfy.com/?={}".format(search_terms))

    @commands.command(hidde=True)
    @commands.guild_only()
    async def hug(self, ctx, user: discord.Member, intensity: int = 1):
        """Because everyone likes hugs

        Up to 10 intensity levels."""
        name = italics(user.display_name)
        if intensity <= 0:
            msg = "(っ˘̩╭╮˘̩)っ" + name
        elif intensity <= 3:
            msg = "(っ´▽｀)っ" + name
        elif intensity <= 6:
            msg = "╰(*´︶`*)╯" + name
        elif intensity <= 9:
            msg = "(つ≧▽≦)つ" + name
        elif intensity >= 10:
            msg = "(づ￣ ³￣)づ{} ⊂(´・ω・｀⊂)".format(name)
        await ctx.send(msg)

    @commands.command()
    @commands.guild_only()
    async def userinfo(self, ctx, *, user: discord.Member = None):
        """Shows user's information"""
        author = ctx.author
        guild = ctx.guild

        if not user:
            user = author

        # A special case for a special someone :^)
        special_date = datetime.datetime(2022, 7, 4, 6, 8, 4, 443000)
        is_special = (user.id == 650898413340327973 and
                      guild.id == 873336207143219231)

        roles = sorted(user.roles)[1:]

        joined_at = user.joined_at if not is_special else special_date
        since_created = (ctx.message.created_at - user.created_at).days
        since_joined = (ctx.message.created_at - joined_at).days
        user_joined = joined_at.strftime("%d %b %Y %H:%M")
        user_created = user.created_at.strftime("%d %b %Y %H:%M")
        member_number = sorted(guild.members,
                               key=lambda m: m.joined_at).index(user) + 1

        created_on = "{}\n({} days ago)".format(user_created, since_created)
        joined_on = "{}\n({} days ago)".format(user_joined, since_joined)

        game = "Chilling in {} status".format(user.status)

        if user.game and user.game.name and user.game.url:
            game = "Streaming: [{}]({})".format(user.game, user.game.url)
        elif user.game and user.game.name:
            game = "Playing {}".format(user.game)

        if roles:
            roles = ", ".join([x.name for x in roles])
        else:
            roles = "None"

        data = discord.Embed(description=game, colour=user.colour)
        data.add_field(name="Joined Discord on", value=created_on)
        data.add_field(name="Joined this server on", value=joined_on)
        data.add_field(name="Roles", value=roles, inline=False)
        data.set_footer(text="Member #{} | User ID: {}"
                             "".format(member_number, user.id))

        name = str(user)
        name = " ~ ".join((name, user.nick)) if user.nick else name

        if user.avatar:
            data.set_author(name=name, url=user.avatar_url)
            data.set_thumbnail(url=user.avatar_url)
        else:
            data.set_author(name=name)

        try:
            await ctx.send(embed=data)
        except discord.HTTPException:
            await ctx.send("I need the `Embed links` permission "
                           "to send this")

    @commands.command()
    @commands.guild_only()
    async def serverinfo(self, ctx):
        """Shows guild's information"""
        guild = ctx.guild
        online = len([m.status for m in guild.members
                      if m.status == discord.Status.online or
                      m.status == discord.Status.idle])
        total_users = len(guild.members)
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        passed = (ctx.message.created_at - guild.created_at).days
        created_at = ("Since {}. That's over {} days ago!"
                      "".format(guild.created_at.strftime("%d %b %Y %H:%M"),
                                passed))

        colour = ''.join([choice('0123456789ABCDEF') for x in range(6)])
        colour = randint(0, 0xFFFFFF)

        data = discord.Embed(
            description=created_at,
            colour=discord.Colour(value=colour))
        data.add_field(name="Region", value=str(guild.region))
        data.add_field(name="Users", value="{}/{}".format(online, total_users))
        data.add_field(name="Text Channels", value=text_channels)
        data.add_field(name="Voice Channels", value=voice_channels)
        data.add_field(name="Roles", value=len(guild.roles))
        data.add_field(name="Owner", value=str(guild.owner))
        data.set_footer(text="Server ID: " + str(guild.id))

        if guild.icon_url:
            data.set_author(name=guild.name, url=guild.icon_url)
            data.set_thumbnail(url=guild.icon_url)
        else:
            data.set_author(name=guild.name)

        try:
            await ctx.send(embed=data)
        except discord.HTTPException:
            await ctx.send("I need the `Embed links` permission "
                           "to send this")

    @commands.command()
    async def urban(self, ctx, *, search_terms: str, definition_number: int=1):
        """Urban Dictionary search
                Definition number must be between 1 and 10"""

        def encode(s):
            return quote_plus(s, encoding='utf-8', errors='replace')

        # definition_number is just there to show up in the help
        # all this mess is to avoid forcing double quotes on the user

        search_terms = search_terms.split(" ")
        try:
            if len(search_terms) > 1:
                pos = int(search_terms[-1]) - 1
                search_terms = search_terms[:-1]
            else:
                pos = 0
            if pos not in range(0, 11):  # API only provides the
                pos = 0  # top 10 definitions
        except ValueError:
            pos = 0

        search_terms = {"term": "+".join([s for s in search_terms])}
        url = "http://api.urbandictionary.com/v0/define"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=search_terms) as r:
                    result = await r.json()
            item_list = result["list"]
            if item_list:
                definition = item_list[pos]['definition']
                example = item_list[pos]['example']
                defs = len(item_list)
                msg = ("**Definition #{} out of {}:\n**{}\n\n"
                       "**Example:\n**{}".format(pos + 1, defs, definition,
                                                 example))
                msg = pagify(msg, ["\n"])
                for page in msg:
                    await ctx.send(page)
            else:
                await ctx.send("Your search terms gave no results.")
        except IndexError:
            await ctx.send("There is no definition #{}".format(pos + 1))
        except:
            await ctx.send("Error.")