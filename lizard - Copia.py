import discord
import json
import os
from discord.ext import commands

TOKEN = "YOUR_TOKEN"
TARGET_PHRASE = "lizard."
DATA_FILE = "count_data.json"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"count": 0, "high_score": 0, "channel_id": None, "last_user_id": None}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

data = load_data()

async def update_presence():
    await bot.change_presence(activity=discord.Game(name=f"Lizard. Count: {data['count']}"))

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await update_presence()

@bot.command()
@commands.has_permissions(administrator=True)
async def setchannel(ctx):
    data["channel_id"] = ctx.channel.id
    save_data(data)
    await ctx.send("✅ Channel set for Lizard. counting!")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    print(f"[DEBUG] {message.channel.id} - {message.author}: {message.content}")

    if data["channel_id"] == message.channel.id:
        content = message.content.lower().strip()

        if content != TARGET_PHRASE:
            await message.add_reaction("❌")
            await message.channel.send(
                f"Chain has been ruined by **{message.author.display_name}** because they said: **{message.content}**"
            )
            data["count"] = 0
            data["last_user_id"] = None
            save_data(data)
            await update_presence()

        elif data["last_user_id"] == message.author.id:
            await message.add_reaction("❌")
            await message.channel.send(
                f"Chain has been ruined by **{message.author.display_name}** because they posted twice in a row."
            )
            data["count"] = 0
            data["last_user_id"] = None
            save_data(data)
            await update_presence()

        else:
            data["count"] += 1
            data["last_user_id"] = message.author.id
            if data["count"] > data["high_score"]:
                data["high_score"] = data["count"]
            save_data(data)
            await message.add_reaction("✅")
            await update_presence()

    await bot.process_commands(message)

bot.run("YOUR_TOKEN")
