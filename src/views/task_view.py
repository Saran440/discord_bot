import discord
from models import update_task_status, assign_task_to_user, delete_task


class TaskDropdown(discord.ui.Select):
    def __init__(self, tasks):
        self.tasks = tasks
        options = [
            discord.SelectOption(label=f"{idx+1}. {(task['task'][:90] + '...') if len(task['task']) > 100 else task['task']}", value=str(task["id"]))

            for idx, task in enumerate(tasks)
        ]
        super().__init__(placeholder="📋 Select a task...", options=options, custom_id="select_task")
    
    async def callback(self, interaction: discord.Interaction):
        task_id = int(self.values[0])
        selected_task = next((task for task in self.tasks if task["id"] == task_id), None)
        if not selected_task:
            await interaction.response.send_message("⚠️ Task not found!", ephemeral=True)
            return

        embed = TaskView.create_embed(self.tasks)

        task_name = selected_task['task']
        if len(task_name) > 1000:
            task_name = selected_task['task'][:1000] + "..."

        embed.add_field(name="\n\n📋 Selected Task", value=f"**{task_name}**", inline=False)

        view = TaskView(self.tasks, selected_task, task_id)
        await interaction.response.edit_message(embed=embed, view=view)


class TaskView(discord.ui.View):
    def __init__(self, tasks=None, selected_task=None, selected_index=None):
        super().__init__(timeout=None)
        self.tasks = tasks or []
        self.selected_task = selected_task
        self.selected_index = selected_index

        self.add_item(TaskDropdown(self.tasks))

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

    async def confirm_task(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if not self.selected_task:
            await interaction.followup.send("⚠️ No task selected!", ephemeral=True)
            return

        new_status = not self.selected_task["done"]
        update_task_status(self.selected_index, new_status)
        self.selected_task["done"] = new_status
        embed = TaskView.create_embed(self.tasks)
        await interaction.message.edit(embed=embed, view=self)

    async def assign_task(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if not self.selected_task:
            await interaction.followup.send("⚠️ No task selected!", ephemeral=True)
            return

        user = interaction.user
        assign_task_to_user(self.selected_index, user.id, user.display_name)
        self.selected_task["assigned"] = user.id
        self.selected_task["assigned_name"] = user.display_name
        embed = TaskView.create_embed(self.tasks)
        await interaction.message.edit(embed=embed, view=self)

    async def remove_task(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if not self.selected_task:
            await interaction.followup.send("⚠️ No task selected!", ephemeral=True)
            return

        delete_task(self.selected_index)

        task_name = self.selected_task["task"]
        if len(task_name) > 1000:
            task_name = task_name[:1000] + "..."
        await interaction.followup.send(f"✅ Task {task_name} deleted!", ephemeral=True)

    @staticmethod
    def create_embed(tasks):
        embed = discord.Embed(title="⭐ To-Do List", color=discord.Color.blue())
        for idx, task in enumerate(tasks):
            status = "✅" if task["done"] else "[ ]"
            assigned = f"📌 {task['assigned_name']}" if task["assigned"] else "⚡ *Not Assigned*"
            created_at = task["created_at"]
            embed.add_field(name=f"{idx+1}. {task['task']}", value=f"{status} {assigned}\n🕒 {created_at}", inline=False)
        return embed

    @staticmethod
    def create_embed(tasks):
        embed = discord.Embed(title="⭐ To-Do List", color=discord.Color.blue())

        for idx, task in enumerate(tasks):
            status = "✅" if task["done"] else "[ ]"
            assigned = f"📌 {task['assigned_name']}" if task["assigned"] else "⚡ *Not Assigned*"
            created_at = task["created_at"]

            # Truncate task name (Discord max 256, but we limit to 240)
            truncated_name = f"{idx+1}. {task['task'][:240]}..." if len(task["task"]) > 250 else f"{idx+1}. {task['task']}"

            # Truncate value (Discord max 1024, but we limit to 1000 to be safe)
            value_content = f"{status} {assigned}\n🕒 {created_at}"
            truncated_value = value_content[:1000] + "..." if len(value_content) > 1000 else value_content

            embed.add_field(name=truncated_name, value=truncated_value, inline=False)

        return embed
