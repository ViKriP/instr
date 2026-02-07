import subprocess
import threading
import flet as ft
from database.crud import get_full_instruction
from ui.components.log_window import build_log_dialog
from core.logger import logger 

@logger.catch(reraise=True) # reraise=True выбросит ошибку дальше, False - подавит её
def _run_process_logic(inst_id, log_view: ft.ListView, page):
    """Внутренняя функция с логикой потоков и subprocess"""
    logger.bind(instruction_id=inst_id).info("Начало выполнения инструкции") # bind добавляет контекст

    def add_log(text, color=ft.Colors.WHITE, is_bold=False):
        """Хелпер для безопасного обновления UI из потока"""
        log_view.controls.append(
            ft.Text(
                text, 
                color=color, 
                weight=ft.FontWeight.BOLD if is_bold else ft.FontWeight.NORMAL,
                font_family="monospace",
                selectable=True
            )
        )
        log_view.update()

    def run_bash(command):
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            # Читаем вывод в реальном времени
            if process.stdout:
                for line in iter(process.stdout.readline, ""):
                    add_log(f"  {line.strip()}", color=ft.Colors.GREY_400)
            
            process.wait()
            return process.returncode
        except Exception as e:
            add_log(f"System Error: {str(e)}", color=ft.Colors.RED)
            return -1

    def worker():
        # 1. Получаем данные
        data = get_full_instruction(inst_id)
        if not data:
            add_log("Error: Инструкция не найдена.", ft.Colors.RED)
            return

        add_log(f"🚀 ЗАПУСК: {data['name']}", ft.Colors.CYAN, True)
        add_log("="*40, ft.Colors.GREY_700)

        # 2. Зависимости
        if data["dependencies"]:
            add_log("📦 Проверка зависимостей...", is_bold=True)
            logger.debug("Запуск проверки зависимостей...")
            for dep in data["dependencies"]:
                add_log(f"Checking: {dep['name']}...", ft.Colors.BLUE_200)
                if dep['check_command']:
                    code = run_bash(dep['check_command'])
                    if code == 0:
                        add_log("  ✅ OK", ft.Colors.GREEN)
                        logger.success(f"Инструкция {inst_id} выполнена успешно!")
                    else:
                        add_log(f"  ⚠️ FAIL (Code {code})", ft.Colors.AMBER)
                        logger.exception(f"Инструкция {inst_id} не выполнена!")
                else:
                    add_log("  ℹ️ Пропущено (нет команды)", ft.Colors.GREY)

        # 3. Задачи
        add_log("-" * 40, ft.Colors.GREY_700)
        for task in data["tasks"]:
            add_log(f"🔹 Задача {task['sequence']}: {task['name']}", ft.Colors.BLUE_100)
            
            for sol in task["solutions"]:
                add_log(f"Exec: {sol['exec_command']}", ft.Colors.GREY_600)
                code = run_bash(sol['exec_command'])
                if code != 0:
                    add_log(f"❌ ОШИБКА ВЫПОЛНЕНИЯ (Code {code})", ft.Colors.RED)
                    add_log("Остановка процесса.", ft.Colors.RED, True)
                    return

        add_log("="*40, ft.Colors.GREY_700)
        add_log("🏁 ВЫПОЛНЕНИЕ ЗАВЕРШЕНО", ft.Colors.GREEN, True)

    # Запускаем поток
    threading.Thread(target=worker, daemon=True).start()

def open_execution_logs(page: ft.Page, inst_id):
    """
    Точка входа:
    1. Создает UI (через build_log_dialog)
    2. Открывает окно
    3. Запускает логику (_run_process_logic)
    """
    # Получаем готовые компоненты из ui/components/log_window.py
    dialog, log_view = build_log_dialog(page)

    # Монтируем и открываем
    if dialog not in page.overlay:
        page.overlay.append(dialog)
    dialog.open = True
    
    page.update()

    # Передаем управление логике, скармливая ей log_view для вывода
    _run_process_logic(inst_id, log_view, page)