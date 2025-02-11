import discord
from discord.ui import View, Select, Button
from models import update_task_status, assign_task_to_user, delete_task

MAX_LIST = 20  # Limit embed 20 rows

class TaskDropdown(discord.ui.Select):
    def __init__(self, tasks, current_page=0):
        self.tasks = tasks
        self.current_page = current_page
        self.tasks_per_page = MAX_LIST
        self.max_page = (len(tasks) - 1) // self.tasks_per_page

        # ตัดรายการตามหน้า
        start = current_page * self.tasks_per_page
        end = start + self.tasks_per_page
        page_tasks = tasks[start:end]

        # สร้างตัวเลือก (ไม่เกิน 20 รายการ)
        options = [
            discord.SelectOption(label=f"{task['id']} {task['task'][:90]}", value=str(task["id"]))
            for task in page_tasks
        ]

        super().__init__(
            placeholder=f"📋 Select a task... (Page {current_page + 1}/{self.max_page + 1})",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        selected_task_id = int(self.values[0])
        selected_task = next((task for task in self.tasks if task["id"] == selected_task_id), None)

        if selected_task:
            embeds = TaskView.create_embeds(self.tasks)
            task_name = selected_task['task']
            if len(task_name) > 1000:
                task_name = selected_task['task'][:1000] + "..."

            # Last embed
            embeds[-1].add_field(name="\n\n📋 Selected Task", value=f"**#{selected_task['id']} {task_name}**", inline=False)
            view = TaskView(self.tasks, selected_task, selected_task_id)
            await interaction.response.edit_message(embed=embeds[-1], view=view)


class TaskView(discord.ui.View):
    def __init__(self, tasks=None, selected_task=None, selected_index=None, current_page=0):
        super().__init__(timeout=None)
        self.tasks = tasks or []
        self.selected_task = selected_task
        self.selected_index = selected_index
        self.current_page = current_page

        # เพิ่ม Dropdown
        self.add_item(TaskDropdown(self.tasks, current_page))

        # ✅ เพิ่มปุ่ม Confirm, Assign, Remove เมื่อมี Task ถูกเลือก
        if selected_task is not None:
            confirm_button = discord.ui.Button(label="✅ Confirm", style=discord.ButtonStyle.green)
            confirm_button.callback = self.confirm_task
            self.add_item(confirm_button)

            assign_button = discord.ui.Button(label="🎯 Assign To", style=discord.ButtonStyle.blurple)
            assign_button.callback = self.assign_task
            self.add_item(assign_button)

            remove_button = discord.ui.Button(label="❌ Clear Task", style=discord.ButtonStyle.danger)
            remove_button.callback = self.remove_task
            self.add_item(remove_button)

        # ✅ เพิ่มปุ่ม Previous ถ้าไม่ใช่หน้าที่แรก
        if current_page > 0:
            self.add_item(PrevPageButton(self.tasks, current_page))

        # ✅ เพิ่มปุ่ม Next ถ้ายังไม่ถึงหน้าสุดท้าย
        if (current_page + 1) * MAX_LIST < len(tasks):
            self.add_item(NextPageButton(self.tasks, current_page))

    async def confirm_task(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if not self.selected_task:
            await interaction.followup.send("⚠️ No task selected!", ephemeral=True)
            return

        new_status = not self.selected_task["done"]
        update_task_status(self.selected_index, new_status)
        self.selected_task["done"] = new_status

        # Update
        embeds = TaskView.create_embeds(self.tasks)
        for embed in embeds:
            await interaction.followup.send(embed=embed, view=self)


    async def assign_task(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if not self.selected_task:
            await interaction.followup.send("⚠️ No task selected!", ephemeral=True)
            return

        user = interaction.user
        assign_task_to_user(self.selected_index, user.id, user.display_name)
        self.selected_task["assigned"] = user.id
        self.selected_task["assigned_name"] = user.display_name

        # Update
        embeds = TaskView.create_embeds(self.tasks)
        for embed in embeds:
            await interaction.followup.send(embed=embed, view=self)


    async def remove_task(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if not self.selected_task:
            await interaction.followup.send("⚠️ No task selected!", ephemeral=True)
            return

        delete_task(self.selected_index)
        await interaction.followup.send(f"✅ Task #{self.selected_index['id']} deleted!", ephemeral=True)

    @staticmethod
    def create_embeds(tasks):
        embeds = []
        
        for i in range(0, len(tasks), MAX_LIST):
            embed = discord.Embed(title="⭐ To-Do List", color=discord.Color.blue())
            chunk = tasks[i:i+MAX_LIST]  # ตัดแบ่ง tasks เป็นชุดละ 20 อัน
            
            for task in chunk:
                status = "✅" if task["done"] else "[ ]"
                assigned = f"📌 {task['assigned_name']}" if task["assigned"] else "⚡ *Not Assigned*"
                created_at = task["created_at"]
                embed.add_field(name=f"#{task['id']} {task['task'][:95]}", value=f"{status} {assigned}\n🕒 {created_at}", inline=False)

            embeds.append(embed)

        return embeds


# ปุ่ม Previous / Next สำหรับเปลี่ยนหน้า
class PrevPageButton(discord.ui.Button):
    def __init__(self, tasks, current_page):
        super().__init__(label="⬅️ Previous", style=discord.ButtonStyle.primary)
        self.tasks = tasks
        self.current_page = current_page

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(view=TaskView(self.tasks, current_page=self.current_page - 1))


class NextPageButton(discord.ui.Button):
    def __init__(self, tasks, current_page):
        super().__init__(label="➡️ Next", style=discord.ButtonStyle.primary)
        self.tasks = tasks
        self.current_page = current_page

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(view=TaskView(self.tasks, current_page=self.current_page + 1))
