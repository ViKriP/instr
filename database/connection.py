import sqlite3

def create_db():
    conn = sqlite3.connect('instructions_app.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Таблицы
    cursor.execute("CREATE TABLE IF NOT EXISTS instructions (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS dependencies (id INTEGER PRIMARY KEY AUTOINCREMENT, instruction_id INTEGER, name TEXT, description TEXT, check_command TEXT, sequence INTEGER, FOREIGN KEY(instruction_id) REFERENCES instructions(id) ON DELETE CASCADE)")
    cursor.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, instruction_id INTEGER, name TEXT, description TEXT, sequence INTEGER, FOREIGN KEY(instruction_id) REFERENCES instructions(id) ON DELETE CASCADE)")
    cursor.execute("CREATE TABLE IF NOT EXISTS solutions (id INTEGER PRIMARY KEY AUTOINCREMENT, task_id INTEGER, solution_type TEXT, exec_command TEXT, FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE)")
    cursor.execute("CREATE TABLE IF NOT EXISTS tags (id INTEGER PRIMARY KEY AUTOINCREMENT, instruction_id INTEGER, name TEXT, FOREIGN KEY(instruction_id) REFERENCES instructions(id) ON DELETE CASCADE)")
    cursor.execute("CREATE TABLE IF NOT EXISTS projects (id INTEGER PRIMARY KEY AUTOINCREMENT, instruction_id INTEGER, name TEXT, FOREIGN KEY(instruction_id) REFERENCES instructions(id) ON DELETE CASCADE)")
    
    conn.commit()
    conn.close()
