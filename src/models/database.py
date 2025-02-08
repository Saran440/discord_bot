import sqlite3

DB_NAME = "todo.db"

def init_db():
    """สร้างตารางหากยังไม่มี"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        channel_id INTEGER,
        task TEXT,
        assigned INTEGER,
        assigned_name TEXT,
        done INTEGER,
        created_at TEXT
    )
    """)
    conn.commit()
    conn.close()

def add_task(channel_id, task, created_at):
    """เพิ่ม Task ลงในฐานข้อมูล"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (channel_id, task, assigned, assigned_name, done, created_at) VALUES (?, ?, ?, ?, ?, ?)", 
                   (channel_id, task, None, None, 0, created_at))
    conn.commit()
    conn.close()

def get_tasks(channel_id):
    """ดึง Task ทั้งหมดของ Channel นั้น"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, task, assigned, assigned_name, done, created_at FROM tasks WHERE channel_id = ?", (channel_id,))
    tasks = cursor.fetchall()
    conn.close()
    return [{"id": row[0], "task": row[1], "assigned": row[2], "assigned_name": row[3], "done": bool(row[4]), "created_at": row[5]} for row in tasks]

def update_task_status(task_id, done):
    """อัปเดตสถานะ Task"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET done = ? WHERE id = ?", (done, task_id))
    conn.commit()
    conn.close()

def assign_task_to_user(task_id, user_id, user_name):
    """อัปเดต Assigned User ของ Task"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET assigned = ?, assigned_name = ? WHERE id = ?", (user_id, user_name, task_id))
    conn.commit()
    conn.close()

def delete_task(task_id):
    """ลบ Task ออกจากฐานข้อมูล"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
