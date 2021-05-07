import discord, asyncpg, random
from data.secrets import secrets
from discord.ext import commands

colours = [0xFFED1B, 0xF1EFE3, 0x00A8FE, 0x1FEDF9, 0x7CF91F, 0xF91F43]

async def get_prefix(client, message):
    base = [f'<@{client.user.id}> ', f'<@!{client.user.id}> ']
    result = await client.prefix_database.fetch("SELECT prefix FROM prefix WHERE guild_id = $1", message.guild.id)
    if not result:
        return ["!", *base]
    if result:
        return [result[0]['prefix'], *base]

client = commands.Bot(
    command_prefix=get_prefix,
    intents=discord.Intents.all(),
    owner_ids=[711444754080071714]
)
client.token = secrets['token']

@client.event
async def on_ready():
    print(f'Logged in as {client.user}.')

async def connect():
    client.prefix_database = await asyncpg.create_pool(
        database="tutorial",
        user="postgres", 
        password=secrets['postgres'], 
        host="127.0.0.1"
    )
    print('Connected to database')

@client.group(name="prefix", aliases=['p', 'pre'])
async def prefix(ctx):
    if ctx.invoked_subcommand is None:
        embed = discord.Embed(color=random.choice(colours), timestamp=ctx.message.created_at)
        embed.set_author(name="Tutorial Bot's prefix system", icon_url=client.user.avatar_url)
        embed.description = """
        1. `set` : Set prefix prefix.
        2. `view` : View the current prefix.
        """
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed)

@prefix.command(name="set")
@commands.check_any(commands.has_permissions(manage_guild=True), commands.is_owner())
async def set(ctx, prefix: str=None):
    if prefix is None:
        return await ctx.send("Enter a new prefix :|")

    result = await client.prefix_database.fetch("SELECT * FROM prefix WHERE guild_id = $1", ctx.guild.id)
    if not result:
        await client.prefix_database.execute("INSERT INTO prefix(guild_id, prefix) VALUES($1, $2)", ctx.guild.id, prefix)
    if result:
        await client.prefix_database.execute("UPDATE prefix SET prefix = $1 WHERE guild_id = $2", prefix, ctx.guild.id)
    await ctx.send(f"Succesully set the prefix to `{prefix}`")

@prefix.command(name="view")
async def view(ctx):
    prefixes = await get_prefix(client, ctx.message)
    embed = discord.Embed(color=random.choice(colours), timestamp=ctx.message.created_at)
    embed.set_author(name=f"{ctx.guild.name}'s prefixes", icon_url=ctx.guild.icon_url)
    embed.description = f"""
    1. {client.user.mention}
    2. `{prefixes[0]}`
    """
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

    await ctx.send(embed=embed)

@client.event
async def on_command_error(ctx, error):
    error = getattr(error, "original", error)

    if isinstance(error, commands.errors.CommandNotFound):
        pass
    elif isinstance(error, commands.errors.CheckAnyFailure):
        await ctx.send("> <:NO:823830259816333394> " + str(error.errors[0]))
    else:
        raise error

client.loop.run_until_complete(connect())
client.run(client.token)