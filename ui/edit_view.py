import flet as ft
from core.logger import logger
from database.crud import (
    get_full_instruction, create_instruction, update_instruction, 
    add_dependency, delete_dependency, add_task_with_solution, delete_task
)

@logger.catch(reraise=True)
def InstructionEditView(page: ft.Page, inst_id=None):
    """
    Страница редактирования.
    Если inst_id is None -> Режим создания новой инструкции.
    Если inst_id есть -> Режим редактирования (доступно добавление задач).
    """
    
    # --- Состояние ---
    is_editing = inst_id is not None
    
    # Поля формы
    name_field = ft.TextField(label="Название инструкции", autofocus=True)
    desc_field = ft.TextField(label="Описание", multiline=True, min_lines=3)
    
    # Контейнеры для списков (будут заполняться только в режиме редактирования)
    dependencies_list = ft.Column()
    tasks_list = ft.Column()

    def load_data():
        if is_editing:
            data = get_full_instruction(inst_id)
            if data:
                name_field.value = data["name"]
                desc_field.value = data["description"]
                
                # Рендер зависимостей
                dependencies_list.controls.clear()
                for dep in data["dependencies"]:
                    dependencies_list.controls.append(
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.MEMORY),
                            title=ft.Text(dep["name"]),
                            subtitle=ft.Text(dep["check_command"], font_family="monospace"),
                            trailing=ft.IconButton(
                                ft.Icons.DELETE, 
                                on_click=lambda _, id=dep["id"]: delete_dep_click(id)
                            )
                        )
                    )

                # Рендер задач
                tasks_list.controls.clear()
                for task in data["tasks"]:
                    # Берем первую команду решения для отображения
                    cmd = task["solutions"][0]["exec_command"] if task["solutions"] else "No command"
                    tasks_list.controls.append(
                        ft.ListTile(
                            leading=ft.CircleAvatar(content=ft.Text(str(task["sequence"]))),
                            title=ft.Text(task["name"]),
                            subtitle=ft.Text(cmd, font_family="monospace"),
                            trailing=ft.IconButton(
                                ft.Icons.DELETE, 
                                on_click=lambda _, id=task["id"]: delete_task_click(id)
                            )
                        )
                    )
            page.update()

    # --- Обработчики Основной формы ---
    def save_instruction(e):
        if not name_field.value:
            name_field.error_text = "Введите название"
            page.update()
            return

        if is_editing:
            update_instruction(inst_id, name_field.value, desc_field.value)
            page.show_dialog(ft.SnackBar(ft.Text("Сохранено!")))
            # page.snack_bar = ft.SnackBar(ft.Text("Сохранено!"))
            # page.snack_bar.open = True
            page.update()
        else:
            new_id = create_instruction(name_field.value, desc_field.value)
            # После создания переходим в режим редактирования этой инструкции
            page.go(f"/edit/{new_id}")

    # --- Диалог добавления Зависимости ---
    dep_name = ft.TextField(label="Название пакета/утилиты")
    dep_cmd = ft.TextField(label="Команда проверки (например: python --version)")
    
    def add_dep_click(e):
        if dep_name.value:
            add_dependency(inst_id, dep_name.value, dep_cmd.value)
            dep_dialog.open = False
            dep_name.value = ""
            dep_cmd.value = ""
            load_data() # Обновляем список
            page.update()

    dep_dialog = ft.AlertDialog(
        title=ft.Text("Добавить зависимость"),
        content=ft.Column([dep_name, dep_cmd], tight=True),
        actions=[ft.TextButton("Добавить", on_click=add_dep_click)]
    )

    def open_dep_dialog(e):
        #page.dialog = dep_dialog
        if dep_dialog not in page.overlay:
            page.overlay.append(dep_dialog)
        dep_dialog.open = True
        page.update()

    def delete_dep_click(dep_id):
        delete_dependency(dep_id)
        load_data()

    # --- Диалог добавления Задачи ---
    task_name = ft.TextField(label="Название шага")
    task_seq = ft.TextField(label="Номер шага", value="1", keyboard_type=ft.KeyboardType.NUMBER)
    task_cmd = ft.TextField(label="Bash команда", multiline=True)

    def add_task_click(e):
        if task_name.value and task_cmd.value:
            add_task_with_solution(inst_id, task_name.value, int(task_seq.value), task_cmd.value)
            task_dialog.open = False
            task_name.value = ""
            task_cmd.value = ""
            # Автоинкремент шага для удобства
            task_seq.value = str(int(task_seq.value) + 1)
            load_data()
            page.update()

    task_dialog = ft.AlertDialog(
        title=ft.Text("Добавить задачу"),
        content=ft.Column([task_seq, task_name, task_cmd], tight=True),
        actions=[ft.TextButton("Добавить", on_click=add_task_click)]
    )

    def open_task_dialog(e):
        #page.dialog = task_dialog
        if task_dialog not in page.overlay:
            page.overlay.append(task_dialog)
        task_dialog.open = True
        page.update()

    def delete_task_click(task_id):
        delete_task(task_id)
        load_data()

    # --- Сборка UI ---
    load_data()

    # Секции зависимостей и задач показываем ТОЛЬКО если мы уже создали инструкцию
    children_sections = []
    if is_editing:
        children_sections = [
            ft.Divider(),
            ft.Row([
                ft.Text("Зависимости", size=20, weight="bold"),
                ft.IconButton(ft.Icons.ADD_CIRCLE, on_click=open_dep_dialog, icon_color="green")
            ], alignment="spaceBetween"),
            dependencies_list,
            
            ft.Divider(),
            ft.Row([
                ft.Text("Задачи (Шаги)", size=20, weight="bold"),
                ft.IconButton(ft.Icons.ADD_CIRCLE, on_click=open_task_dialog, icon_color="blue")
            ], alignment="spaceBetween"),
            tasks_list
        ]

    return ft.View(route=f"/edit/{inst_id}" if inst_id else "/create", controls=[
        ft.AppBar(
            title=ft.Text("Редактор инструкции" if is_editing else "Новая инструкция"),
            actions=[ft.IconButton(ft.Icons.SAVE, on_click=save_instruction)]
        ),
        ft.Column([
            name_field,
            desc_field,
            ft.ElevatedButton("Сохранить основное", on_click=save_instruction),
            *children_sections
        ], scroll="adaptive")
    ])