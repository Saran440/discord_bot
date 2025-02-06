import discord
import os

from discord.ext import commands
from discord.ui import View, Button
from dotenv import load_dotenv  # โหลดไลบรารี dotenv

# โหลดค่า .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")  # ดึงค่า TOKEN จาก .env

bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())

todo_list = []  # เก็บรายการ Todo

class TodoButton(Button):
    def __init__(self, label, index):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.index = index
        self.completed = False

    async def callback(self, interaction: discord.Interaction):
        self.completed = not self.completed
        self.label = f"~~{todo_list[self.index]['task']}~~" if self.completed else todo_list[self.index]['task']
        self.style = discord.ButtonStyle.success if self.completed else discord.ButtonStyle.primary
        await interaction.response.edit_message(view=self.view)

class TodoView(View):
    def __init__(self):
        super().__init__()
        self.update_buttons()
    
    def update_buttons(self):
        self.clear_items()
        for index, item in enumerate(todo_list):
            self.add_item(TodoButton(label=item['task'], index=index))

@bot.command()
async def add(ctx, task: str, member: discord.Member = None):
    """เพิ่มงานใหม่ใน To-do list และกำหนดให้คนอื่นได้"""
    todo_list.append({"task": task, "assigned": member})
    view = TodoView()
    await ctx.send(f"**To-Do List:**", view=view)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

bot.run(TOKEN)
