import flet as ft
from database.crud import get_all_instructions, get_full_instruction
from logic.executor import open_log_window

def HomeView(page: ft.Page):
    items = get_all_instructions()
    list_items = ft.Column(scroll="adaptive", expand=True)
    
    for item in items:
        list_items.controls.append(
            ft.ListTile(
                title=ft.Text(item["name"]),
                subtitle=ft.Text(item["description"]),
                on_click=lambda _, id=item["id"]: page.go(f"/detail/{id}")
            )
        )

    return ft.View(route="/", controls=[
        ft.AppBar(title=ft.Text("Мои инструкции"), bgcolor=ft.Colors.ON_SURFACE_VARIANT),
        list_items
    ])

def DetailView(page: ft.Page, inst_id):
    data = get_full_instruction(inst_id)
    return ft.View(route=f"/detail/{inst_id}", controls=[
        ft.AppBar(title=ft.Text(data["name"])),
        ft.Column([
            ft.Text(data["description"], italic=True),
            ft.Divider(),
            ft.Text("Задачи:", weight="bold"),
            *[ft.Text(f"{t['sequence']}. {t['name']}") for t in data["tasks"]],
            ft.ElevatedButton("ВЫПОЛНИТЬ", icon=ft.Icons.PLAY_ARROW, 
                             on_click=lambda _: open_log_window(page, inst_id))
        ], scroll="adaptive", expand=True)
    ])
