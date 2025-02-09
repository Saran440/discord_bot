import os
import discord
from dotenv import load_dotenv
import pytz

# โหลดค่าจาก .env
load_dotenv()

# Token และ Timezone
TOKEN = os.getenv("DISCORD_TOKEN")
TIMEZONE = os.getenv("TIMEZONE", "UTC")
TIMEZONE_OBJ = pytz.timezone(TIMEZONE)

# ตั้งค่า Intents ของ Discord
INTENTS = discord.Intents.default()
INTENTS.message_content = True
INTENTS.guilds = True  # สำหรับ Assign Users
