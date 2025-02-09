import discord
from discord import app_commands
from models import add_task, get_tasks, delete_task, assign_task_to_user
from views import TaskView
from datetime import datetime
from utils.config import TIMEZONE_OBJ


class TaskGroup(app_commands.Group):
    """Group command for managing tasks"""

    def __init__(self):
        super().__init__(name="task", description="Manage tasks")

    @app_commands.command(name="add", description="Add a new task")
    async def add_task(self, interaction: discord.Interaction, task: str):
        """Add a Task"""
        await interaction.response.defer()
        created_at = datetime.now(TIMEZONE_OBJ).strftime("%Y-%m-%d %H:%M")
        add_task(interaction.channel.id, task, created_at)

        if len(task) > 1000:
            task = task[:1000] + "..."
        await self.update_task_list(interaction, f"✅ Task added: **{task}**")

    @app_commands.command(name="clear", description="Clear a specific task")
    async def clear_task(self, interaction: discord.Interaction, task_name: str):
        """Clear a Task"""
        await interaction.response.defer()
        tasks = get_tasks(interaction.channel.id)
        task_to_clear = next((task for task in tasks if task["task"] == task_name), None)

        if task_to_clear:
            delete_task(task_to_clear["id"])
            await self.update_task_list(interaction, f"🗑 Task removed: **{task_name}**")
        else:
            await interaction.followup.send("⚠️ Task not found!", ephemeral=True)

    @app_commands.command(name="show", description="Show all tasks or tasks assigned to a user")
    async def show_tasks(self, interaction: discord.Interaction, assigned_to: discord.Member = None):
        """Show tasks, either all or assigned to a user"""
        await interaction.response.defer()
        tasks = get_tasks(interaction.channel.id)

        if assigned_to:
            filtered_tasks = [task for task in tasks if task["assigned"] == assigned_to.id]
            if filtered_tasks:
                embed = TaskView.create_embed(filtered_tasks)
                await interaction.followup.send(embed=embed, view=TaskView(filtered_tasks))
            else:
                await interaction.followup.send(f"⚠️ No tasks assigned to {assigned_to.mention}", ephemeral=True)
        else:
            if not tasks:
                await interaction.followup.send("📌 No tasks available!", ephemeral=True)
                return
            
            embed = TaskView.create_embed(tasks)
            await interaction.followup.send(embed=embed, view=TaskView(tasks))

    @app_commands.command(name="assign", description="Assign or remove assignment from a task")
    async def assign_task_command(self, interaction: discord.Interaction, task_index: int, user: discord.Member = None):
        """Assign a task to a user or remove assignment if no user is provided"""
        await interaction.response.defer()

        tasks = get_tasks(interaction.channel.id)
        if not tasks:
            await interaction.followup.send("⚠️ No tasks available!", ephemeral=True)
            return
        
        if task_index < 1 or task_index > len(tasks):
            await interaction.followup.send("⚠️ Invalid task index!", ephemeral=True)
            return

        task_selected = tasks[task_index - 1]

        if user:
            assign_task_to_user(task_selected["id"], user.id, user.display_name)
            await self.update_task_list(interaction, f"🎯 Task **{task_selected['task']}** assigned to {user.mention}")
        else:
            assign_task_to_user(task_selected["id"], None, None)  # Remove assignment
            await self.update_task_list(interaction, f"❌ Task **{task_selected['task']}** assignment removed.")

    async def update_task_list(self, interaction: discord.Interaction, message: str = None):
        """Update Task List and edit the latest bot message"""
        tasks = get_tasks(interaction.channel.id)

        if not tasks:
            await interaction.followup.send("📌 No tasks available!", ephemeral=True)
            return
        embed = TaskView.create_embed(tasks)
        response = await interaction.followup.send(embed=embed, view=TaskView(tasks))
        if message:
            await interaction.channel.send(message)