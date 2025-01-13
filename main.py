########
from enum import Enum
import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
########
from database.db import *
########

load_dotenv()

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents) 

welcome_channel_id = int(os.getenv("WELCOME_CHANNEL"))
welcome_message_id = int(os.getenv("WELCOME_MESSAGE_ID"))
welcome_gaming_channel_id = int(os.getenv("WELCOME_GAMING_CHANNEL"))
welcome_gaming_message_id = int(os.getenv("WELCOME_GAMING_MESSAGE_ID"))
lord_poptarts_id = int(os.getenv("LORD_POPTARTS_ID"))
mod_role = str(os.getenv("MOD_ROLE"))

class ChannelType(str, Enum):
    WELCOME = "welcome"
    WELCOME_GAMING = "gaming"

@bot.event
async def on_ready():
    print(f'Bot is online as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands to the guild.")
    except Exception as e:
        print(f"Error syncing commmands: {str(e)}")


@bot.tree.command(name="request", description="puts in a request for a new channel to be created")
async def request(ctx: discord.Interaction, channel_suggestion: str, justification: str):
    try:
        # Get the user object for your Discord user ID
        user = await bot.fetch_user(lord_poptarts_id)
        
        # Send a direct message (DM) to yourself
        await user.send(f"New request from {ctx.user.name}:\n Channel suggestion: {channel_suggestion}\nJustification: {justification}")
        
        # Respond to the user in the channel
        await ctx.response.send_message(content="Your request has been sent!", ephemeral=True)
    
    except Exception as e:
        await ctx.response.send_message(content=f"Failed to send your request: {str(e)}", ephemeral=True)


@bot.tree.command(name="add_role", description="Adds a new role to the DB and emoji to the proper welcome channel.")
@commands.has_role(mod_role)
async def add_role(ctx: discord.Interaction, emoji: str, role_name: str, channel: ChannelType):

    channel_name = channel.value

    # Make sure the role doesn't already exist in the server
    if discord.utils.get(ctx.guild.roles, name=role_name) is not None:
        await ctx.response.send_message(content=f'Role {role_name} already exists in the server. Either remove this role from the server or choose a new role name', ephemeral=True)
        return
    
    # Make sure the role isn't already in use in the server
    if get_row_by_role(channel_name, role_name) is not None:
        await ctx.response.send_message(content=f'{role_name} role already in use by {get_row_by_role(channel, role_name)}', ephemeral=True)
        return

    # Make sure that emoji isn't already in use in the channel
    if get_row_by_emoji(channel_name, emoji) is not None:
        await ctx.response.send_message(content=f'{emoji} emoji already in use by {get_row_by_emoji(channel, emoji)}', ephemeral=True)
        return

    # Add the role to the server
    role = await ctx.guild.create_role(name=role_name)

    # # add the emoji and role to the DB
    add_row(channel_name, emoji, role.name)

    # Get the proper welcome message
    message = None
    if channel_name == ChannelType.WELCOME.value:
        welcomeChannel = bot.get_channel(welcome_channel_id)
        message = await welcomeChannel.fetch_message(welcome_message_id)
    elif channel_name == ChannelType.WELCOME_GAMING.value:
        welcomeChannel = bot.get_channel(welcome_gaming_channel_id)
        message = await welcomeChannel.fetch_message(welcome_gaming_message_id)

    # Unable to update the welcome message unless I make the bot the sender of the message.
    # This would also mean we would need to delete the current message that is in the welcome channels
    # Causing everyone to have to re-add their emojis Creating a bit of chaos.
    # I am not going to do this at this time, but if I start over at some point I will add this and just make the bot the one who sends the message.
    # updated_message = add_role_to_message(message.content, emoji, role.name)
    # await message.edit(content=updated_message)
    
    # Add the emoji to the proper welcome channel message
    await message.add_reaction(emoji)

    # Successful Response
    await ctx.response.send_message(content=f'{emoji}: {role.name} has been added. Remember to assign this role to a channel.', ephemeral=True)
    user = await bot.fetch_user(lord_poptarts_id)
    await user.send(f"New request from {ctx.user.name}:\n Update {channel_name} message to include {emoji}:  {role.name}")
    return

@bot.tree.command(name="remove_role", description="Removes emoji and role from the DB.")
@commands.has_role(mod_role)
async def remove_role(ctx: discord.Interaction, emoji: str, channel: ChannelType, reason: str):

    # Make sure the emoji exists in channel
    row = get_row_by_emoji(channel.value, emoji)
    if row is None:
        await ctx.response.send_message(content=f'{emoji} Not found in DB', ephemeral=True)
        return

    role = row[1]

    # Remove role from server (if not already deleted)
    fetched_role = discord.utils.get(ctx.guild.roles, name=role)
    if fetched_role is not None:
        await fetched_role.delete(reason=reason)

    # Remove the emoji and role from the DB
    remove_row(channel.value, emoji)

    # Get the proper welcome message
    message = None
    if channel.value == ChannelType.WELCOME.value:
        welcomeChannel = bot.get_channel(welcome_channel_id)
        message = await welcomeChannel.fetch_message(welcome_message_id)
    elif channel.value == ChannelType.WELCOME_GAMING.value:
        welcomeChannel = bot.get_channel(welcome_gaming_channel_id)
        message = await welcomeChannel.fetch_message(welcome_gaming_message_id)

    # Edit the text removing the emoji and role from the proper welcome channel message
    # Unable to update the welcome message unless I make the bot the sender of the message.
    # This would also mean we would need to delete the current message that is in the welcome channels
    # Causing everyone to have to re-add their emojis Creating a bit of chaos.
    # I am not going to do this at this time, but if I start over at some point I will add this and just make the bot the one who sends the message.
    # updated_message = remove_role_from_message(message.content, emoji, role.name)
    # await message.edit(content=updated_message)

    # Remove the emoji from the proper welcome channel message
    await message.clear_reaction(emoji) 

    # Successful response
    await ctx.response.send_message(content=f'{emoji} has been removed.', ephemeral=True)
    user = await bot.fetch_user(lord_poptarts_id)
    await user.send(f"New request from {ctx.user.name}:\n Update {channel.value} message to remove {emoji}:  {role}")
    return

@bot.event
async def on_raw_reaction_add(payload):
    table = None
    # Check if the reaction is on the watched message
    if payload.message_id == welcome_message_id:
        table = "welcome"
    elif payload.message_id == welcome_gaming_message_id:
        table = "gaming"
    else:
        return

    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id) if guild else None
    if member is None:
        try:
            member = await guild.fetch_member(payload.user_id) if guild else None
        except discord.NotFound:
            print(f"Member with ID {payload.user_id} not found.")
            return

    if guild is None or member is None or member.bot:
        return

    # Check if the emoji is in the mapping
    role_name = get_row_by_emoji(table, payload.emoji.name)
    if role_name is not None:
        role = discord.utils.get(guild.roles, name=role_name)

        if role:
            await member.add_roles(role)
            print(f"Assigned {role_name} to {member.name}")
        else:
            print(f'role {role} does not exist in the discord')
    else:
        print(f'emoji {payload.emoji.name} not found in table {table}')


@bot.event
async def on_raw_reaction_remove(payload):
    table = None
    # Check if the reaction is on the watched message
    if payload.message_id == welcome_message_id:
        table = "welcome"
    elif payload.message_id == welcome_gaming_message_id:
        table = "gaming"
    else:
        return

    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id) if guild else None
    if member is None:
        try:
            member = await guild.fetch_member(payload.user_id) if guild else None
        except discord.NotFound:
            print(f"Member with ID {payload.user_id} not found.")
            return

    if guild is None or member is None or member.bot:
        return

    emoji = payload.emoji.name

    # Check if the emoji is in the mapping
    role_name = get_row_by_emoji(table, payload.emoji.name)
    if role_name is not None:
        role = discord.utils.get(guild.roles, name=role_name)

        if role:
            await member.remove_roles(role)
            print(f"Removed {role_name} from {member.name}")
        else:
            print(f'role {role} does not exist in the discord')
    else:
        print(f'emoji {payload.emoji.name} not found in table {table}')
    

bot.run(os.getenv("BOT_KEY"))