import discord
from datetime import datetime
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import pytz
import os

# โหลดค่า TOKEN และ TIMEZONE จาก .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
TIMEZONE = os.getenv("TIMEZONE", "UTC")
TIMEZONE_OBJ = pytz.timezone(TIMEZONE)

# เปิด Intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True  # ต้องใช้สำหรับการ Assign Users

bot = commands.Bot(command_prefix="!", intents=intents)

# เก็บ To-Do List
todo_list = []  # เช่น {"task": "ทำงาน", "assigned": None, "done": False, "created_at": "2025-02-06 15:30"}

class TaskDropdown(discord.ui.Select):
    """Dropdown สำหรับเลือก Task"""
    def __init__(self):
        options = [
            discord.SelectOption(label=f"{'✅ ' if task['done'] else '[ ] '}{task['task']}",
                                 value=str(idx))
            for idx, task in enumerate(todo_list)
        ]
        super().__init__(placeholder="📋 เลือกงาน...", options=options, custom_id="select_task")
    
    async def callback(self, interaction: discord.Interaction):
        idx = int(self.values[0])
        selected_task = todo_list[idx]

        embed = TaskView.create_embed()
        embed.add_field(name="\n\n📋 งานที่เลือก", value=f"**{selected_task['task']}**", inline=False)

        view = TaskView(selected_task, idx)
        await interaction.response.edit_message(embed=embed, view=view)


class TaskView(discord.ui.View):
    """View สำหรับปุ่มจัดการ Task"""
    def __init__(self, selected_task=None, selected_index=None):
        super().__init__(timeout=None)
        self.selected_task = selected_task
        self.selected_index = selected_index

        # Dropdown เลือกงาน
        self.add_item(TaskDropdown())

        if selected_task is not None:
            # ปุ่ม Confirm
            confirm_button = discord.ui.Button(label="✅ Confirm", style=discord.ButtonStyle.green)
            confirm_button.callback = self.confirm_task
            self.add_item(confirm_button)

            # ปุ่ม Assign
            assign_button = discord.ui.Button(label="🎯 Assign To", style=discord.ButtonStyle.blurple)
            assign_button.callback = self.assign_task
            self.add_item(assign_button)

            # ปุ่มลบ Task
            remove_button = discord.ui.Button(label="❌ Clear Task", style=discord.ButtonStyle.danger)
            remove_button.callback = self.remove_task
            self.add_item(remove_button)

    async def confirm_task(self, interaction: discord.Interaction):
        """เปลี่ยนสถานะ Task เป็น Done/Not Done"""
        idx = self.selected_index
        todo_list[idx]["done"] = not todo_list[idx]["done"]

        embed = TaskView.create_embed()
        view = TaskView(todo_list[idx], idx)
        await interaction.response.edit_message(embed=embed, view=view)

    async def assign_task(self, interaction: discord.Interaction):
        """Assign งานให้คนที่กดปุ่ม"""
        idx = self.selected_index
        user = interaction.user

        todo_list[idx]["assigned"] = user.id
        todo_list[idx]["assigned_name"] = user.display_name

        embed = TaskView.create_embed()
        view = TaskView(todo_list[idx], idx)
        await interaction.response.edit_message(embed=embed, view=view)

    async def remove_task(self, interaction: discord.Interaction):
        """ลบ Task ที่เลือก"""
        idx = self.selected_index
        removed_task = todo_list.pop(idx)

        if not todo_list:
            await interaction.response.edit_message(content="📌 ไม่มีงานที่ต้องทำ!", embed=None, view=None)
        else:
            embed = TaskView.create_embed()
            view = TaskView()
            await interaction.response.edit_message(embed=embed, view=view)

        await interaction.followup.send(f"❌ ลบงาน: **{removed_task['task']}** เรียบร้อย!", ephemeral=True)

    @staticmethod
    def create_embed():
        """สร้าง Embed แสดง To-Do List ทั้งหมด"""
        embed = discord.Embed(title="⭐ To-Do List", color=discord.Color.blue())
        for idx, task in enumerate(todo_list):
            status = "✅" if task["done"] else "[ ]"
            assigned = f"📌 {task['assigned_name']}" if task["assigned"] else "⚡ *Not Assigned*"
            created_at = task["created_at"]
            embed.add_field(name=f"{idx+1}. {task['task']}", value=f"{status} {assigned}\n🕒 {created_at}", inline=False)
        return embed

async def update_task_list(interaction: discord.Interaction):
    """อัปเดต To-Do List และส่งข้อความใหม่"""
    if not todo_list:
        await interaction.followup.send("📌 ไม่มีงานที่ต้องทำ!", ephemeral=True)
    else:
        embed = TaskView().create_embed()
        await interaction.followup.send(embed=embed, view=TaskView())

@bot.tree.command(name="add_task", description="เพิ่มงานเข้า To-Do List")
async def add_task(interaction: discord.Interaction, task: str):
    """เพิ่ม Task ใหม่"""
    await interaction.response.defer()
    created_at = datetime.now(TIMEZONE_OBJ).strftime("%Y-%m-%d %H:%M")
    todo_list.append({"task": task, "assigned": None, "assigned_name": None, "done": False, "created_at": created_at})
    # await interaction.followup.send(f"✅ เพิ่มงาน: **{task}** (🕒 {created_at}) เรียบร้อย!")
    await update_task_list(interaction)

@bot.tree.command(name="clear_task", description="ลบ Task ที่เลือก")
async def clear_task(interaction: discord.Interaction, task_index: int):
    """ลบ Task ที่เลือกออกจาก To-Do List"""
    await interaction.response.defer()
    
    if 0 <= task_index < len(todo_list):
        removed_task = todo_list.pop(task_index)
        await interaction.followup.send(f"❌ ลบงาน: **{removed_task['task']}** เรียบร้อย!")
    else:
        await interaction.followup.send("⚠️ ไม่พบ Task ที่เลือก!", ephemeral=True)
    
    # อัปเดต Task List
    await update_task_list(interaction)

@bot.tree.command(name="show_tasks", description="แสดงรายการงานที่ค้างอยู่")
async def show_tasks(interaction: discord.Interaction):
    """แสดง Task List"""
    await interaction.response.defer()
    if not todo_list:
        await interaction.followup.send("📌 ไม่มีงานที่ต้องทำ!", ephemeral=True)
    else:
        embed = TaskView.create_embed()
        await interaction.followup.send(embed=embed, view=TaskView())


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} commands.")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")

@bot.event
async def on_message(message):
    # เช็คถ้าข้อความมาจาก API
    if message.content == "📩 **คุณได้รับอีเมลใหม่!**":
        task = message.embeds[0].title
        created_at = datetime.now(TIMEZONE_OBJ).strftime("%Y-%m-%d %H:%M")  # เวลาสร้าง Task
        # Task limit 80 character
        todo_list.append({"task": task[:80], "assigned": None, "done": False, "created_at": created_at})
        
        # ส่ง Task List ใหม่
        if todo_list:
            embed = TaskView().create_embed()
            await message.channel.send(embed=embed, view=TaskView())
        return  # ไม่ให้ Bot ตอบตัวเอง 

    await bot.process_commands(message)

bot.run(TOKEN)
