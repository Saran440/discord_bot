import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from keep_alive import keep_alive  # Import Web Server
import os

# โหลดค่า TOKEN จาก .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

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
        todo_list[idx]["assigned_name"] = user.name

        # อัปเดต UI ใหม่
        new_view = TaskView()
        await interaction.response.edit_message(embed=self.create_embed(), view=new_view)

    def create_embed(self):
        """สร้าง Embed แสดง To-Do List"""
        embed = discord.Embed(title="📌 To-Do List", color=discord.Color.blue())
        for idx, task in enumerate(todo_list):
            status = "✅" if task["done"] else "[ ]"
            assigned = f"📌 {task['assigned_name']}" if task["assigned"] else "⚡ *Not Assigned*"
            embed.add_field(name=f"{idx+1}. {task['task']}", value=f"{status} {assigned}", inline=False)
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
    todo_list.append({"task": task, "assigned": None, "assigned_name": None, "done": False})
    await interaction.followup.send(f"✅ เพิ่มงาน: **{task}** เรียบร้อย!")


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
    if message.author == bot.user and message.content.startswith("BOT_API: "):
        task = message.content.replace("BOT_API: ", "").strip()
        todo_list.append({"task": task, "assigned": None, "done": False})
        await message.channel.send(f"✅ เพิ่มงาน: **{task}** เรียบร้อย!")
        return  # ไม่ให้ Bot ตอบตัวเอง 

    await bot.process_commands(message)

keep_alive()
bot.run(TOKEN)
