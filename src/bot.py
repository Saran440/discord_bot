import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

from datetime import datetime

# Import คำสั่งที่แยกไว้
from commands import TaskGroup, MusicBot
from models import init_db, add_task, get_tasks
from utils.config import TOKEN, INTENTS, TIMEZONE_OBJ
from views import TaskView

# โหลด .env
load_dotenv()

# สร้าง Bot
bot = commands.Bot(command_prefix="!", intents=INTENTS)

@bot.event
async def on_ready():
    init_db()  # สร้างฐานข้อมูลถ้ายังไม่มี
    # bot.add_cog(MusicBot(bot))  # ✅ เพิ่ม MusicBot cog
    # bot.tree.add_command(MusicBot())  # เพิ่มคำสั่ง /task
    await bot.add_cog(MusicBot(bot))
    bot.tree.add_command(TaskGroup())  # เพิ่มคำสั่ง /task
    await bot.tree.sync()
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_message(message):
    """เช็คข้อความจาก API และเพิ่ม Task ลงในฐานข้อมูล"""
    if message.content == "📩 **คุณได้รับอีเมลใหม่!**" and message.embeds:
        task = message.embeds[0].title
        created_at = datetime.now(TIMEZONE_OBJ).strftime("%Y-%m-%d %H:%M")  # เวลาสร้าง Task
        
        # บันทึกลงฐานข้อมูล
        add_task(message.channel.id, task, created_at)

        # ดึงข้อมูลใหม่จากฐานข้อมูล
        tasks = get_tasks(message.channel.id)
        
        # สร้าง Embed และอัปเดต To-Do List
        if tasks:
            embeds = TaskView.create_embeds(tasks)
            for embed in embeds:
                await message.channel.send(embed=embed, view=TaskView(tasks))

        return  # ไม่ให้ Bot ตอบตัวเอง 

    await bot.process_commands(message)

bot.run(TOKEN)
