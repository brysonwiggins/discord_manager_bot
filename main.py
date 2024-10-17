########
import json
import discord
import os
from database.loldle_repo import get_loldle_data
from dotenv import load_dotenv
from discord.ext import commands
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
########
from models.LoldleData import LoldleData
from util import DAILY_STATS_FOLDER, get_today_date, get_todays_answers, save_submission
########

load_dotenv()

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents) 

loldle_channel_id = int(os.getenv("LOLDLE_CHANNEL_ID"))
welcome_message_id = int(os.getenv("WELCOME_MESSAGE_ID"))
welcome_gaming_message_id = int(os.getenv("WELCOME_GAMING_MESSAGE_ID"))
lord_poptarts_id = int(os.getenv("LORD_POPTARTS_ID"))
mst = timezone('America/Denver')

emoji_to_role_welcome = {
    '🎰': 'Daily Games',
    '🤪': 'Memes',
    '🤳': 'Tik Toks',
    '🖨️': '3D Printing',
    '🥞': 'Food',
    '🎵': 'Music',
    'Mario_Dab': 'Gaming',
}

emoji_to_role_gaming = {
    '🤬': 'LOL',
    'Mario_TPose': 'SM64',
    '🔒': 'Deadlock',
    '🌫️': 'Enshrouded'
}

# Ensure folders exist
os.makedirs(DAILY_STATS_FOLDER, exist_ok=True)

async def new_day_task():
    # Get the current time to display in the message
    fetchedAnswers = get_todays_answers()

@bot.event
async def on_ready():
    print(f'Bot is online as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands to the guild.")
    except Exception as e:
        print(f"Error syncing commmands: {str(e)}")

    # scheduler = AsyncIOScheduler()
    # scheduler.add_job(new_day_task, CronTrigger(hour=0, minute=1, timezone=mst))
    # scheduler.start()

@bot.tree.command(name="get_answers", description="This will return todays answers, but will mark you as forfeit if you haven't submitted yours!")
async def submit(ctx: discord.Interaction):

    fetchedAnswers = get_todays_answers()
    submitted = get_loldle_data(get_today_date(), ctx.user.id)
    alreadySubmitted = False
    for submission in submitted:
        if(submission['userId'] == ctx.user.id):
            alreadySubmitted = True
            break
    
    if not alreadySubmitted:
        save_submission(ctx.user.id, None)

    await ctx.response.send_message(fetchedAnswers.pretty_print())
    

@bot.tree.command(name="submit", description="submit your loldle submission for the day.")
async def submit(ctx: discord.Interaction, submission: str):
    print(submission)
    try:
        data = LoldleData()
        data.parse_loldle_submission(submission)
        print(data.__dict__)
        if(data.is_valid_submission()):
            save_submission(ctx.user.id,  data)
            await ctx.response.send_message(f"{ctx.user.name} has submitted their LoLdle results for today.")
        else:
            await ctx.response.send_message(f"{ctx.user.name}, your submission was incorrectly formatted")

    except Exception as e:
        await ctx.response.send_message(f"Error processing submission: {str(e)}")


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



@bot.event
async def on_raw_reaction_add(payload):
    emoji_to_role = []
    # Check if the reaction is on the watched message
    if payload.message_id == welcome_message_id:
        emoji_to_role = emoji_to_role_welcome
    elif payload.message_id == welcome_gaming_message_id:
        emoji_to_role = emoji_to_role_gaming
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
    if emoji in emoji_to_role:
        role_name = emoji_to_role[emoji]
        role = discord.utils.get(guild.roles, name=role_name)

        if role:
            await member.add_roles(role)
            print(f"Assigned {role_name} to {member.name}")


@bot.event
async def on_raw_reaction_remove(payload):
    emoji_to_role = []
    # Check if the reaction is on the watched message
    if payload.message_id == welcome_message_id:
        emoji_to_role = emoji_to_role_welcome
    elif payload.message_id == welcome_gaming_message_id:
        emoji_to_role = emoji_to_role_gaming
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
    if emoji in emoji_to_role:
        role_name = emoji_to_role[emoji]
        role = discord.utils.get(guild.roles, name=role_name)

        if role:
            await member.remove_roles(role)
            print(f"Removed {role_name} from {member.name}")

    

bot.run(os.getenv("BOT_KEY"))