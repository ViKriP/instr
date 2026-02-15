import flet as ft
from database.crud import (
    get_full_instruction, create_instruction, update_instruction, delete_instruction,
    add_dependency, update_dependency, delete_dependency, 
    add_task_with_solution, update_task_with_solution, delete_task
)

def InstructionEditView(page: ft.Page, inst_id=None):
    is_editing = inst_id is not None
    
    # Состояние для редактирования/удаления
    editing_dep_id = None 
    editing_task_id = None
    pending_delete_id = None
    pending_delete_type = None

    # Поля UI
    name_field = ft.TextField(label="Название инструкции", autofocus=True)
    desc_field = ft.TextField(label="Описание", multiline=True, min_lines=3)
    dependencies_list = ft.Column()
    tasks_list = ft.Column()

    # --- Вспомогательная функция для открытия диалогов через Overlay ---
    def open_modal(modal):
        if modal not in page.overlay:
            page.overlay.append(modal)
        modal.open = True
        page.update()

    def close_modal(modal):
        modal.open = False
        page.update()

    # ==================================================================================
    # 1. ДИАЛОГ ЗАВИСИМОСТЕЙ
    # ==================================================================================
    dep_name = ft.TextField(label="Название пакета")
    dep_cmd = ft.TextField(label="Команда проверки")
    
    def save_dep_click(e):
        if dep_name.value:
            if editing_dep_id:
                update_dependency(editing_dep_id, dep_name.value, dep_cmd.value)
            else:
                add_dependency(inst_id, dep_name.value, dep_cmd.value)
            close_modal(dep_dialog)
            load_data()

    dep_action_btn = ft.TextButton("Добавить", on_click=save_dep_click)
    dep_dialog = ft.AlertDialog(
        content=ft.Column([dep_name, dep_cmd], tight=True, width=400),
        actions=[
            ft.TextButton("Отмена", on_click=lambda _: close_modal(dep_dialog)),
            dep_action_btn
        ]
    )

    def open_dep_edit(e, dep_data=None):
        nonlocal editing_dep_id
        if dep_data:
            editing_dep_id = dep_data["id"]
            dep_name.value = dep_data["name"]
            dep_cmd.value = dep_data["check_command"]
            dep_dialog.title = ft.Text("Редактировать зависимость")
            dep_action_btn.text = "Сохранить"
        else:
            editing_dep_id = None
            dep_name.value = ""
            dep_cmd.value = ""
            dep_dialog.title = ft.Text("Добавить зависимость")
            dep_action_btn.text = "Добавить"
        open_modal(dep_dialog)

    # ==================================================================================
    # 2. ДИАЛОГ ЗАДАЧ
    # ==================================================================================
    task_name = ft.TextField(label="Название шага")
    task_seq = ft.TextField(label="№", width=60, keyboard_type=ft.KeyboardType.NUMBER)
    task_cmd = ft.TextField(label="Bash команда", multiline=True, min_lines=3)

    def save_task_click(e):
        if task_name.value and task_cmd.value:
            try: seq = int(task_seq.value)
            except: seq = 1
            if editing_task_id:
                update_task_with_solution(editing_task_id, task_name.value, seq, task_cmd.value)
            else:
                add_task_with_solution(inst_id, task_name.value, seq, task_cmd.value)
            close_modal(task_dialog)
            load_data()

    task_action_btn = ft.TextButton("Добавить", on_click=save_task_click)
    task_dialog = ft.AlertDialog(
        content=ft.Column([ft.Row([task_seq, task_name]), task_cmd], tight=True, width=500),
        actions=[
            ft.TextButton("Отмена", on_click=lambda _: close_modal(task_dialog)),
            task_action_btn
        ]
    )

    def open_task_edit(e, task_data=None):
        nonlocal editing_task_id
        if task_data:
            editing_task_id = task_data["id"]
            task_name.value = task_data["name"]
            task_seq.value = str(task_data["sequence"])
            cmd = task_data["solutions"][0]["exec_command"] if task_data["solutions"] else ""
            task_cmd.value = cmd
            task_dialog.title = ft.Text("Редактировать задачу")
            task_action_btn.text = "Сохранить"
        else:
            editing_task_id = None
            task_name.value = ""
            task_seq.value = str(len(tasks_list.controls) + 1)
            task_cmd.value = ""
            task_dialog.title = ft.Text("Добавить задачу")
            task_action_btn.text = "Добавить"
        open_modal(task_dialog)

    # ==================================================================================
    # 3. ПОДТВЕРЖДЕНИЕ УДАЛЕНИЯ (Child & Main)
    # ==================================================================================
    def execute_child_delete(e):
        if pending_delete_type == "dep": delete_dependency(pending_delete_id)
        else: delete_task(pending_delete_id)
        close_modal(child_del_modal)
        load_data()

    child_del_text = ft.Text()
    child_del_modal = ft.AlertDialog(
        title=ft.Text("Удаление"),
        content=child_del_text,
        actions=[
            ft.TextButton("Отмена", on_click=lambda _: close_modal(child_del_modal)),
            ft.ElevatedButton("Удалить", on_click=execute_child_delete, bgcolor=ft.Colors.RED, color=ft.Colors.WHITE)
        ]
    )

    def req_child_del(id, name, type_):
        nonlocal pending_delete_id, pending_delete_type
        pending_delete_id, pending_delete_type = id, type_
        child_del_text.value = f"Удалить '{name}'?"
        open_modal(child_del_modal)

    # Главное удаление
    def execute_main_delete(e):
        delete_instruction(inst_id)
        close_modal(main_del_modal)
        page.go("/")

    main_del_text = ft.Text()
    main_del_modal = ft.AlertDialog(
        title=ft.Text("Удалить инструкцию?"),
        content=main_del_text,
        actions=[
            ft.TextButton("Отмена", on_click=lambda _: close_modal(main_del_modal)),
            ft.ElevatedButton("Удалить всё", on_click=execute_main_delete, bgcolor=ft.Colors.RED, color=ft.Colors.WHITE)
        ]
    )

    def req_main_del(e):
        data = get_full_instruction(inst_id)
        main_del_text.value = f"Вы уверены, что хотите удалить '{data['name']}' со всеми задачами?"
        open_modal(main_del_modal)

    # ==================================================================================
    # 4. РЕНДЕР И СБОРКА
    # ==================================================================================
    def load_data():
        if not is_editing: return
        data = get_full_instruction(inst_id)
        if not data: return
        
        name_field.value, desc_field.value = data["name"], data["description"]
        
        dependencies_list.controls = [
            ft.ListTile(
                leading=ft.Icon(ft.Icons.MEMORY, color=ft.Colors.BLUE_GREY),
                title=ft.Text(d["name"]),
                subtitle=ft.Text(value=d["check_command"], size=12, font_family="monospace"),
                trailing=ft.Row([
                    ft.IconButton(ft.Icons.EDIT, on_click=lambda _, d=d: open_dep_edit(None, d)),
                    ft.IconButton(ft.Icons.DELETE, on_click=lambda _, d=d: req_child_del(d["id"], d["name"], "dep"))
                ], width=100)
            ) for d in data["dependencies"]
        ]

        tasks_list.controls = [
            ft.ListTile(
                leading=ft.CircleAvatar(content=ft.Text(str(t["sequence"]))),
                title=ft.Text(t["name"]),
                subtitle=ft.Text(value=t["solutions"][0]["exec_command"] if t["solutions"] else "No command", 
                                 max_lines=1, 
                                 overflow=ft.TextOverflow.ELLIPSIS, 
                                 font_family="monospace"
                ),
                trailing=ft.Row([
                    ft.IconButton(ft.Icons.EDIT, on_click=lambda _, t=t: open_task_edit(None, t)),
                    ft.IconButton(ft.Icons.DELETE, on_click=lambda _, t=t: req_child_del(t["id"], t["name"], "task"))
                ], width=100)
            ) for t in data["tasks"]
        ]
        page.update()

    def save_instruction(e):
        if not name_field.value: return
        if is_editing:
            update_instruction(inst_id, name_field.value, desc_field.value)
            page.show_dialog(ft.SnackBar(ft.Text("Сохранено")))
            page.update()
        else:
            new_id = create_instruction(name_field.value, desc_field.value)
            page.go(f"/edit/{new_id}")

    load_data()

    app_bar_actions = [ft.IconButton(ft.Icons.SAVE, on_click=save_instruction)]
    if is_editing:
        app_bar_actions.insert(1, ft.IconButton(ft.Icons.DELETE_FOREVER, icon_color=ft.Colors.RED, on_click=req_main_del))

    return ft.View(route=f"/edit/{inst_id}" if inst_id else "/create", controls=[
        ft.AppBar(title=ft.Text("Редактор"), actions=app_bar_actions),
        ft.Column([
            name_field, desc_field,
            ft.ElevatedButton("Сохранить изменения", icon=ft.Icons.SAVE, on_click=save_instruction),
            ft.Divider(height=20),
            ft.Row([ft.Text("Зависимости", size=20, weight="bold"), 
                    ft.IconButton(ft.Icons.ADD_CIRCLE, on_click=lambda e: open_dep_edit(e, None), icon_color=ft.Colors.GREEN)], 
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            dependencies_list,
            ft.Divider(height=20),
            ft.Row([ft.Text("Задачи", size=20, weight="bold"), 
                    ft.IconButton(ft.Icons.ADD_CIRCLE, on_click=lambda e: open_task_edit(e, None), icon_color=ft.Colors.BLUE)], 
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            tasks_list
        ], scroll="adaptive", expand=True)
    ])
