import sqlite3

DB_PATH = "instructions_app.db" # Или путь из конфига

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_all_instructions():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM instructions").fetchall()
    conn.close()
    return rows

def get_full_instruction(inst_id):
    conn = get_db_connection()
    inst = conn.execute("SELECT * FROM instructions WHERE id = ?", (inst_id,)).fetchone()
    if not inst: return None
    
    res = dict(inst)
    res["dependencies"] = [dict(r) for r in conn.execute("SELECT * FROM dependencies WHERE instruction_id = ? ORDER BY sequence", (inst_id,)).fetchall()]
    
    # Задачи + Решения
    tasks = []
    task_rows = conn.execute("SELECT * FROM tasks WHERE instruction_id = ? ORDER BY sequence", (inst_id,)).fetchall()
    for tr in task_rows:
        t = dict(tr)
        t["solutions"] = [dict(s) for s in conn.execute("SELECT * FROM solutions WHERE task_id = ?", (t["id"],)).fetchall()]
        tasks.append(t)
    
    res["tasks"] = tasks
    res["tags"] = [r["name"] for r in conn.execute("SELECT name FROM tags WHERE instruction_id = ?", (inst_id,)).fetchall()]
    res["projects"] = [r["name"] for r in conn.execute("SELECT name FROM projects WHERE instruction_id = ?", (inst_id,)).fetchall()]
    conn.close()
    return res

def add_demo_data():
    """Функция для наполнения базы, чтобы было что тестировать"""
    conn = get_db_connection()
    # Проверяем, есть ли уже данные
    if not conn.execute("SELECT id FROM instructions").fetchone():
        cursor = conn.cursor()
        cursor.execute("INSERT INTO instructions (name, description) VALUES (?,?)", ("Демо-инструкция", "Пример выполнения Bash-команд"))
        iid = cursor.lastrowid
        cursor.execute("INSERT INTO dependencies (instruction_id, name, check_command, sequence) VALUES (?,?,?,?)", (iid, "Версия Python", "python3 --version", 1))
        cursor.execute("INSERT INTO tasks (instruction_id, name, sequence) VALUES (?,?,?)", (iid, "Вывод даты", 1))
        cursor.execute("INSERT INTO solutions (task_id, solution_type, exec_command) VALUES (?,?,?)", (iid, "Bash", "date"))
        cursor.execute("INSERT INTO tags (instruction_id, name) VALUES (?,?)", (iid, "demo"))
        cursor.execute("INSERT INTO projects (instruction_id, name) VALUES (?,?)", (iid, "TestProject"))
        conn.commit()
    conn.close()



def execute_query(query, params=()):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid

# --- INSTRUCTIONS ---
def create_instruction(name, description):
    return execute_query("INSERT INTO instructions (name, description) VALUES (?, ?)", (name, description))

def update_instruction(inst_id, name, description):
    execute_query("UPDATE instructions SET name = ?, description = ? WHERE id = ?", (name, description, inst_id))

def delete_instruction(inst_id):
    # Каскадное удаление (если в БД настроено ON DELETE CASCADE, то это не нужно, но для надежности)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("DELETE FROM instructions WHERE id = ?", (inst_id,))
        conn.commit()

# --- DEPENDENCIES ---
def add_dependency(inst_id, name, command):
    execute_query("INSERT INTO dependencies (instruction_id, name, check_command) VALUES (?, ?, ?)", (inst_id, name, command))

def delete_dependency(dep_id):
    execute_query("DELETE FROM dependencies WHERE id = ?", (dep_id,))

# --- TASKS & SOLUTIONS ---
def add_task_with_solution(inst_id, name, sequence, exec_command):
    # Транзакция: создаем задачу и сразу решение к ней
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (instruction_id, name, sequence) VALUES (?, ?, ?)", (inst_id, name, sequence))
        task_id = cursor.lastrowid
        # По умолчанию создаем Bash решение
        cursor.execute("INSERT INTO solutions (task_id, solution_type, exec_command) VALUES (?, ?, ?)", (task_id, 'bash', exec_command))
        conn.commit()

def delete_task(task_id):
    execute_query("DELETE FROM tasks WHERE id = ?", (task_id,))
