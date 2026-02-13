import flet as ft
from core.logger import logger
from database.crud import (
    get_full_instruction, create_instruction, update_instruction, delete_instruction,
    add_dependency, delete_dependency, add_task_with_solution, delete_task,
    update_dependency, update_task_with_solution
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

    # --- Состояние редактирования дочерних элементов ---
    # Если None - режим добавления. Если ID - режим редактирования.
    editing_dep_id = None 
    editing_task_id = None

    def load_data():
        if is_editing:
            data = get_full_instruction(inst_id)
            if data:
                name_field.value = data["name"]
                desc_field.value = data["description"]
                
                # Рендер Зависимостей
                dependencies_list.controls.clear()
                for dep in data["dependencies"]:
                    dependencies_list.controls.append(
                        ft.ListTile(
                            leading=ft.Icon(icon=ft.Icons.MEMORY, color=ft.Colors.BLUE_GREY),
                            title=ft.Text(value=dep["name"]),
                            subtitle=ft.Text(value=dep["check_command"], size=12, font_family="monospace"),
                            trailing=ft.Row(controls=[
                                # Кнопка РЕДАКТИРОВАТЬ
                                ft.IconButton(
                                    icon=ft.Icons.EDIT, 
                                    icon_color=ft.Colors.BLUE,
                                    on_click=lambda _, d=dep: open_dep_dialog(None, d)
                                ),
                                # Кнопка УДАЛИТЬ
                                ft.IconButton(
                                    icon=ft.Icons.DELETE, 
                                    icon_color=ft.Colors.RED_300,
                                    on_click=lambda _, id=dep["id"]: delete_dep_click(id)
                                ),
                            ], alignment=ft.MainAxisAlignment.END, width=100)
                        )
                    )
                
                # Рендер Задач
                tasks_list.controls.clear()
                for task in data["tasks"]:
                    cmd = task["solutions"][0]["exec_command"] if task["solutions"] else "No command"
                    tasks_list.controls.append(
                        ft.ListTile(
                            leading=ft.CircleAvatar(content=ft.Text(value=str(task["sequence"]))),
                            title=ft.Text(value=task["name"]),
                            subtitle=ft.Text(value=cmd, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, font_family="monospace"),
                            trailing=ft.Row(controls=[
                                # Кнопка РЕДАКТИРОВАТЬ
                                ft.IconButton(
                                    icon=ft.Icons.EDIT, 
                                    icon_color=ft.Colors.BLUE,
                                    on_click=lambda _, t=task: open_task_dialog(None, t)
                                ),
                                # Кнопка УДАЛИТЬ
                                ft.IconButton(
                                    icon=ft.Icons.DELETE, 
                                    icon_color=ft.Colors.RED_300,
                                    on_click=lambda _, id=task["id"]: delete_task_click(id)
                                ),
                            ], alignment=ft.MainAxisAlignment.END, width=100)
                        )
                    )
                
            page.update()

    # --- Обработчики Основной формы ---
    def save_instruction(e):
        if not name_field.value:
            name_field.error = "Введите название"
            page.update()
            return

        if is_editing:
            update_instruction(inst_id, name_field.value, desc_field.value)
            page.show_dialog(ft.SnackBar(ft.Text(value="Инструкция обновлена")))
            page.update()
        else:
            new_id = create_instruction(name_field.value, desc_field.value)
            # После создания переходим в режим редактирования этой инструкции
            page.go(f"/edit/{new_id}")

    # --- Диалог добавления Зависимости ---
    dep_name = ft.TextField(label="Название пакета")
    dep_cmd = ft.TextField(label="Команда проверки")
    
    def add_dep_click(e):
        if dep_name.value:
            add_dependency(inst_id, dep_name.value, dep_cmd.value)
            dep_dialog.open = False
            dep_name.value = ""
            dep_cmd.value = ""
            load_data() # Обновляем список
            page.update()

    dep_dialog = ft.AlertDialog(
        title=ft.Text(value="Добавить зависимость"),
        content=ft.Column(controls=[dep_name, dep_cmd], tight=True),
        actions=[ft.TextButton(content="Добавить", on_click=add_dep_click)]
    )

    def open_dep_dialog(e, dep_data=None):
        """Открывает диалог. Если передан dep_data — заполняет поля."""
        nonlocal editing_dep_id
        if dep_data:
            # Режим РЕДАКТИРОВАНИЯ
            editing_dep_id = dep_data["id"]
            dep_name.value = dep_data["name"]
            dep_cmd.value = dep_data["check_command"]
            dep_dialog.title = ft.Text(value="Редактировать зависимость")
            dep_action_btn.text = "Сохранить"
        else:
            # Режим СОЗДАНИЯ
            editing_dep_id = None
            dep_name.value = ""
            dep_cmd.value = ""
            dep_dialog.title = ft.Text(value="Добавить зависимость")
            dep_action_btn.text = "Добавить"

        #page.dialog = dep_dialog
        if dep_dialog not in page.overlay:
            page.overlay.append(dep_dialog)
        dep_dialog.open = True
        page.update()

    def save_dep_click(e):
        if dep_name.value:
            if editing_dep_id:
                # UPDATE
                update_dependency(editing_dep_id, dep_name.value, dep_cmd.value)
            else:
                # INSERT
                add_dependency(inst_id, dep_name.value, dep_cmd.value)
            
            dep_dialog.open = False
            load_data() # Перерисовать список
            page.update()

    dep_action_btn = ft.TextButton(content="Добавить", on_click=save_dep_click)
    dep_dialog = ft.AlertDialog(
        content=ft.Column(controls=[dep_name, dep_cmd], tight=True, width=400),
        actions=[dep_action_btn]
    )

    def delete_dep_click(dep_id):
        delete_dependency(dep_id)
        load_data()

    # --- Диалог добавления Задачи ---
    task_seq = ft.TextField(label="№", width=70, keyboard_type=ft.KeyboardType.NUMBER)
    task_name = ft.TextField(label="Название шага")
    task_cmd = ft.TextField(label="Bash команда", multiline=True, min_lines=3)

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
        title=ft.Text(value="Добавить задачу"),
        content=ft.Column(controls=[task_seq, task_name, task_cmd], tight=True),
        actions=[ft.TextButton(content="Добавить", on_click=add_task_click)]
    )

    def open_task_dialog(e, task_data=None):
        nonlocal editing_task_id
        if task_data:
            # Режим РЕДАКТИРОВАНИЯ
            editing_task_id = task_data["id"]
            task_name.value = task_data["name"]
            task_seq.value = str(task_data["sequence"])
            # Берем команду из первого решения (упрощение)
            cmd = task_data["solutions"][0]["exec_command"] if task_data["solutions"] else ""
            task_cmd.value = cmd
            
            task_dialog.title = ft.Text(value="Редактировать задачу")
            task_action_btn.text = "Сохранить"
        else:
            # Режим СОЗДАНИЯ
            editing_task_id = None
            task_name.value = ""
            # Автоматически ставим следующий номер
            next_seq = len(tasks_list.controls) + 1
            task_seq.value = str(next_seq)
            task_cmd.value = ""
            
            task_dialog.title = ft.Text(value="Добавить задачу")
            task_action_btn.text = "Добавить"

        if task_dialog not in page.overlay:
            page.overlay.append(task_dialog)
        task_dialog.open = True
        page.update()

    def save_task_click(e):
        if task_name.value and task_cmd.value:
            try:
                seq = int(task_seq.value)
            except:
                seq = 1

            if editing_task_id:
                # UPDATE
                update_task_with_solution(editing_task_id, task_name.value, seq, task_cmd.value)
            else:
                # INSERT
                add_task_with_solution(inst_id, task_name.value, seq, task_cmd.value)

            task_dialog.open = False
            load_data()
            page.update()

    task_action_btn = ft.TextButton(content="Добавить", on_click=save_task_click)
    task_dialog = ft.AlertDialog(
        content=ft.Column(controls=[
            ft.Row(controls=[task_seq, task_name], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            task_cmd
        ], tight=True, width=500),
        actions=[task_action_btn]
    )

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
            ft.Row(controls=[
                ft.Text(value="Зависимости", size=20, weight="bold"),
                ft.IconButton(icon=ft.Icons.ADD_CIRCLE, on_click=lambda e: open_dep_dialog(e, None), icon_color="green")
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            dependencies_list,
            ft.Divider(),
            
            ft.Row(controls=[
                ft.Text(value="Задачи", size=20, weight="bold"),
                ft.IconButton(icon=ft.Icons.ADD_CIRCLE, on_click=lambda e: open_task_dialog(e, None), icon_color="blue")
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            tasks_list
        ]

    # --- Логика удаления из режима редактирования ---
    def confirm_delete_current(e):
        delete_instruction(inst_id)
        confirm_dialog.open = False
        page.show_dialog(ft.SnackBar(ft.Text("Инструкция удалена")))
        # После удаления возвращаемся на главную
        page.go("/") 

    def open_delete_dialog_current(e):
        # Получаем актуальные данные (они уже загружены в load_data, 
        # но для точности берем из UI списков или базы)
        data = get_full_instruction(inst_id)
        if data:
            dep_count = len(data['dependencies'])
            task_count = len(data['tasks'])
            
            del_title.value = f"Удалить '{data['name']}'?"
            del_content.value = (
                f"Будут удалены:\n"
                f"- Зависимостей: {dep_count}\n"
                f"- Задач: {task_count}"
            )
            if confirm_dialog not in page.overlay:
                page.overlay.append(confirm_dialog)
            confirm_dialog.open = True
            page.update()

    # Компоненты диалога
    del_title = ft.Text()
    del_content = ft.Text()
    confirm_dialog = ft.AlertDialog(
        title=del_title,
        content=del_content,
        actions=[
            ft.TextButton("Отмена", on_click=lambda e: setattr(confirm_dialog, 'open', False) or page.update()),
            ft.ElevatedButton("Удалить", bgcolor="red", color="white", on_click=confirm_delete_current),
        ],
        actions_alignment=ft.MainAxisAlignment.END
    )

    # --- Сборка Actions для AppBar ---
    app_bar_actions = [
        ft.IconButton(ft.Icons.SAVE, tooltip="Сохранить", on_click=save_instruction)
    ]
    
    # Если это редактирование, добавляем кнопку Удалить
    if is_editing:
        app_bar_actions.insert(0, 
            ft.IconButton(
                ft.Icons.DELETE_FOREVER, 
                tooltip="Удалить инструкцию", 
                icon_color="red", 
                on_click=open_delete_dialog_current
            )
        )

    return ft.View(route=f"/edit/{inst_id}" if inst_id else "/create", controls=[
        ft.AppBar(
            title=ft.Text(value="Редактор" if is_editing else "Новая инструкция"),
            actions=app_bar_actions # Используем наш список кнопок
        ),
        ft.Column(controls=[
            name_field, desc_field,
            ft.ElevatedButton(content="Сохранить основное", on_click=save_instruction),
            *children_sections
        ], scroll="adaptive", expand=True)
    ])
