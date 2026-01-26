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
    log_view = ft.ListView(expand=True, spacing=2, padding=10, auto_scroll=True)

    # --- Функции обработчики ---

    def clear_logs(e):
        """Очищает содержимое списка логов"""
        log_view.controls.clear()
        page.update()

    async def copy_all_logs(e):
        """Собирает текст изо всех строк и копирует в буфер обмена"""
        # Извлекаем текст из каждого контрола Text в списке
        full_log_text = "\n".join([c.value for c in log_view.controls if isinstance(c, ft.Text)])
        
        if full_log_text:
            await page.clipboard.set(full_log_text)
            # Показываем уведомление пользователю
            page.show_dialog(    
                ft.SnackBar(ft.Text("Лог успешно скопирован в буфер обмена!"), bgcolor=ft.Colors.GREEN_700)
            )
            page.update()
        else:
            page.show_dialog(
                ft.SnackBar(ft.Text("Лог пуст, нечего копировать."), bgcolor=ft.Colors.RED_700)
            )

    def close_dialog(e):
        dialog.open = False
        page.update()


    # --- Создание диалогового окна ---  

    dialog = ft.AlertDialog(
        title=ft.Text("Логи выполнения"),
        content=ft.Container(content=log_view, width=600, height=400, bgcolor=ft.Colors.BLACK, border_radius=5,),
        actions=[
            # Кнопка Копировать
            ft.TextButton(
                "Копировать весь лог", 
                icon=ft.Icons.COPY, 
                on_click=copy_all_logs
            ),
            # Кнопка Очистить
            ft.TextButton(
                "Очистить", 
                icon=ft.Icons.DELETE_SWEEP, 
                icon_color=ft.Colors.RED_400,
                on_click=clear_logs
            ),
            # Кнопка Закрыть
            ft.TextButton("Закрыть", on_click=close_dialog),
            #ft.TextButton("Закрыть", on_click=lambda _: setattr(dialog, "open", False) or page.update())
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    if dialog not in page.overlay:
        page.overlay.append(dialog)
    dialog.open = True
    page.update()
    execute_instruction(inst_id, log_view)
