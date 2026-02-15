import flet as ft
from database.crud import get_all_instructions, get_full_instruction, delete_instruction
from logic.executor import open_execution_logs


def HomeView(page: ft.Page):
    # 1. Контейнер для списка (чтобы можно было его очищать и обновлять)
    list_items = ft.Column(scroll="adaptive", expand=True)
    
    # Переменная для хранения ID удаляемого элемента
    delete_target_id = None

    # --- Диалог подтверждения ---
    def confirm_delete_click(e):
        if delete_target_id:
            delete_instruction(delete_target_id)
            # Закрываем диалог
            confirm_dialog.open = False
            page.show_dialog(ft.SnackBar(ft.Text("Инструкция удалена"), bgcolor=ft.Colors.RED_700))
            # Обновляем список на экране
            load_items()
            page.update()

    def close_dialog(e):
        confirm_dialog.open = False
        page.update()

    # Элементы диалога (текст будем менять динамически)
    del_title = ft.Text("Подтверждение")
    del_content = ft.Text("")

    confirm_dialog = ft.AlertDialog(
        title=del_title,
        content=del_content,
        actions=[
            ft.TextButton("Отмена", on_click=close_dialog),
            ft.ElevatedButton("Удалить", on_click=confirm_delete_click, color="white", bgcolor="red"),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    # --- Логика кнопки "Удалить" ---
    def open_delete_dialog(inst_id):
        nonlocal delete_target_id
        delete_target_id = inst_id
        
        # Получаем статистику перед удалением
        data = get_full_instruction(inst_id)
        if data:
            dep_count = len(data['dependencies'])
            task_count = len(data['tasks'])
            
            del_title.value = f"Удалить '{data['name']}'?"
            del_content.value = (
                f"Вы уверены?\n\n"
                f"• Зависимостей: {dep_count}\n"
                f"• Задач (шагов): {task_count}\n\n"
                f"Это действие необратимо."
            )
            
            if confirm_dialog not in page.overlay:
                page.overlay.append(confirm_dialog)
            confirm_dialog.open = True
            page.update()

    # --- Загрузка списка ---
    def load_items():
        list_items.controls.clear()
        items = get_all_instructions()
        if not items:
            list_items.controls.append(ft.Text("Нет инструкций. Создайте первую!", italic=True))
        
        for item in items:
            list_items.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.DESCRIPTION, color=ft.Colors.BLUE),
                    title=ft.Text(item["name"], weight="bold"),
                    subtitle=ft.Text(item["description"], max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    on_click=lambda _, id=item["id"]: page.go(f"/detail/{id}"),
                    trailing=ft.Row(controls=[
                        # Кнопка Запуска
                        ft.IconButton(
                            icon=ft.Icons.PLAY_ARROW, 
                            tooltip="Запустить",
                            icon_color="green",
                            on_click=lambda _, id=item["id"]: open_execution_logs(page, id)
                        ),
                        # Кнопка Редактирования
                        ft.IconButton(
                            icon=ft.Icons.EDIT,
                            tooltip="Редактировать",
                            icon_color="orange",
                            on_click=lambda _, id=item["id"]: page.go(f"/edit/{id}")),
                        # Кнопка Удаления
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE, 
                            tooltip="Удалить",
                            icon_color="red",
                            on_click=lambda _, id=item["id"]: open_delete_dialog(id)
                        )
                    ], alignment=ft.MainAxisAlignment.END, width=200)
                )
            )
            list_items.controls.append(ft.Divider(height=1, thickness=0.5))

    # Первичная загрузка
    load_items()

    return ft.View(route="/", controls=[
        ft.AppBar(title=ft.Text("Мои инструкции", color=ft.Colors.BLACK), bgcolor=ft.Colors.ON_SURFACE_VARIANT),
        list_items,
        ft.FloatingActionButton(icon=ft.Icons.ADD, on_click=lambda _: page.go("/create"))
    ])

def DetailView(page: ft.Page, inst_id):
    data = get_full_instruction(inst_id)
    return ft.View(route=f"/detail/{inst_id}", controls=[
        ft.AppBar(title=ft.Text(data["name"])),
        ft.Column(controls=[
            ft.Text(data["description"], italic=True),
            ft.IconButton(icon=ft.Icons.EDIT, icon_color="orange", on_click=lambda _: page.go(f"/edit/{inst_id}")),
            ft.Divider(),
            ft.Text("Зависимости:", weight="bold"),
            *[ft.Text(f"{d['name']} \n ({d['check_command']})") for d in data["dependencies"]],
            ft.Divider(),
            ft.Text("Задачи:", weight="bold"),
            *[ft.Text(f"{t['sequence']}. {t['name']} \n {t["solutions"][0]["exec_command"] if t["solutions"] else "No command"} ") for t in data["tasks"]],
            ft.ElevatedButton("ВЫПОЛНИТЬ", 
                              icon=ft.Icons.PLAY_ARROW, 
                              on_click=lambda _: open_execution_logs(page, inst_id))
        ], scroll="adaptive", expand=True)
    ])
