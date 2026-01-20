import subprocess, threading, flet as ft
from database.crud import get_full_instruction

def execute_instruction(inst_id, log_view: ft.ListView):
    def add_log(msg, color=ft.Colors.WHITE):
        log_view.controls.append(ft.Text(msg, color=color, font_family="monospace"))
        log_view.update()

    def run_worker():
        data = get_full_instruction(inst_id)
        add_log(f">>> Запуск: {data['name']}", ft.Colors.CYAN)
        
        for dep in data['dependencies']:
            add_log(f"Проверка: {dep['name']}...")
            res = subprocess.run(dep['check_command'], shell=True, capture_output=True, text=True)
            add_log(res.stdout or res.stderr)
            
        for task in data['tasks']:
            add_log(f"Задача {task['sequence']}: {task['name']}", ft.Colors.AMBER)
            for sol in task['solutions']:
                proc = subprocess.Popen(sol['exec_command'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                for line in proc.stdout:
                    add_log(f"  {line.strip()}")
                proc.wait()
        add_log(">>> Готово", ft.Colors.GREEN)

    threading.Thread(target=run_worker, daemon=True).start()

def open_log_window(page: ft.Page, inst_id):
    log_view = ft.ListView(expand=True, spacing=2)
    dialog = ft.AlertDialog(
        title=ft.Text("Логи выполнения"),
        content=ft.Container(log_view, width=600, height=400, bgcolor=ft.Colors.BLACK),
        actions=[ft.TextButton("Закрыть", on_click=lambda _: setattr(dialog, "open", False) or page.update())]
    )

    if dialog not in page.overlay:
        page.overlay.append(dialog)
    dialog.open = True
    page.update()
    execute_instruction(inst_id, log_view)
