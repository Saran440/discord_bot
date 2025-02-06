import discord
from datetime import datetime  # ใช้เก็บวันที่สร้าง Task
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from keep_alive import keep_alive  # Import Web Server
import pytz
import os

# โหลดค่า TOKEN จาก .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# โหลดค่า Timezone จาก .env
TIMEZONE = os.getenv("TIMEZONE", "UTC")  # ถ้าไม่มีค่าให้ใช้ UTC
TIMEZONE_OBJ = pytz.timezone(TIMEZONE)

# เปิด Intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# เก็บ To-Do List
todo_list = []  # เช่น {"task": "ทำงาน", "assigned": None, "done": False}

class TaskView(discord.ui.View):
    """สร้าง UI ปุ่มให้กับแต่ละงาน"""
    def __init__(self):
        super().__init__(timeout=None)
        self.update_buttons()

    def update_buttons(self):
        """อัปเดตปุ่มให้ตรงกับสถานะของ Task"""
        self.clear_items()  # ลบปุ่มเก่าออกก่อน
        for idx, task in enumerate(todo_list):
            # ปุ่มทำเครื่องหมายว่าเสร็จหรือไม่
            button_done = discord.ui.Button(
                label=f"{'✅ ' if task['done'] else ''}{task['task']}",
                custom_id=f"toggle_{idx}",
                style=discord.ButtonStyle.green if task["done"] else discord.ButtonStyle.secondary,
                row=idx
            )
            button_done.callback = self.toggle_task
            self.add_item(button_done)

            # ปุ่ม Assign งาน
            button_assign = discord.ui.Button(
                label="🎯 Assign",
                custom_id=f"assign_{idx}",
                style=discord.ButtonStyle.blurple,
                row=idx
            )
            button_assign.callback = self.assign_task
            self.add_item(button_assign)

            # ปุ่มลบ Task
            button_remove = discord.ui.Button(
                label="❌ Remove",
                custom_id=f"remove_{idx}",
                style=discord.ButtonStyle.danger,
                row=idx
            )
            button_remove.callback = self.remove_task
            self.add_item(button_remove)

    async def toggle_task(self, interaction: discord.Interaction):
        """เปลี่ยนสถานะ Task เมื่่อกดปุ่ม"""
        idx = int(interaction.data["custom_id"].split("_")[1])
        todo_list[idx]["done"] = not todo_list[idx]["done"]

        # อัปเดต UI ใหม่
        new_view = TaskView()
        await interaction.response.edit_message(embed=self.create_embed(), view=new_view)

    async def assign_task(self, interaction: discord.Interaction):
        """Assign งานให้คนที่กดปุ่ม"""
        idx = int(interaction.data["custom_id"].split("_")[1])
        user = interaction.user

        # อัปเดต Assigned
        todo_list[idx]["assigned"] = user.id
        todo_list[idx]["assigned_name"] = user.display_name

        # อัปเดต UI ใหม่
        new_view = TaskView()
        await interaction.response.edit_message(embed=self.create_embed(), view=new_view)

    async def remove_task(self, interaction: discord.Interaction):
        """ลบ Task ออกจาก To-Do List"""
        idx = int(interaction.data["custom_id"].split("_")[1])
        removed_task = todo_list.pop(idx)  # ลบ Task ที่เลือก

        if not todo_list:
            await interaction.response.edit_message(content="📌 ไม่มีงานที่ต้องทำ!", embed=None, view=None)
        else:
            new_view = TaskView()
            await interaction.response.edit_message(embed=self.create_embed(), view=new_view)

        await interaction.followup.send(f"❌ ลบงาน: **{removed_task['task']}** เรียบร้อย!", ephemeral=True)

    def create_embed(self):
        """สร้าง Embed แสดง To-Do List"""
        embed = discord.Embed(title="⭐ To-Do List", color=discord.Color.blue())
        for idx, task in enumerate(todo_list):
            status = "✅" if task["done"] else "[ ]"
            assigned = f"📌 {task['assigned_name']}" if task["assigned"] else "⚡ *Not Assigned*"
            created_at = task["created_at"]
            embed.add_field(name=f"{idx+1}. {task['task']}", value=f"{status} {assigned}\n🕒 {created_at}", inline=False)
        return embed


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} commands.")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")


@bot.tree.command(name="add_task", description="เพิ่มงานเข้า To-Do List โดยไม่ต้อง Assign")
async def add_task(interaction: discord.Interaction, task: str):
    """เพิ่ม Task ใหม่"""
    await interaction.response.defer()
    created_at = datetime.now(TIMEZONE_OBJ).strftime("%Y-%m-%d %H:%M")  # เวลาสร้าง Task
    todo_list.append({"task": task, "assigned": None, "assigned_name": None, "done": False, "created_at": created_at})
    await interaction.followup.send(f"✅ เพิ่มงาน: **{task}** (🕒 {created_at}) เรียบร้อย!")


@bot.tree.command(name="show_tasks", description="แสดงรายการงานที่ค้างอยู่")
async def show_tasks(interaction: discord.Interaction):
    """แสดง Task List"""
    await interaction.response.defer()
    if not todo_list:
        await interaction.followup.send("📌 ไม่มีงานที่ต้องทำ!", ephemeral=True)
    else:
        embed = TaskView().create_embed()
        await interaction.followup.send(embed=embed, view=TaskView())

@bot.event
async def on_message(message):
    # เช็คถ้าข้อความมาจาก API
    if message.content == "📩 **คุณได้รับอีเมลใหม่!**":
        task = message.embeds[0].title
        created_at = datetime.now(TIMEZONE_OBJ).strftime("%Y-%m-%d %H:%M")  # เวลาสร้าง Task
        todo_list.append({"task": task, "assigned": None, "done": False, "created_at": created_at})
        await message.channel.send(f"✅ เพิ่มงาน: **{task}** (🕒 {created_at}) เรียบร้อย!")
        return  # ไม่ให้ Bot ตอบตัวเอง 

    await bot.process_commands(message)

keep_alive()
bot.run(TOKEN)
