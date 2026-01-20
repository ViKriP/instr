import flet as ft
from database.connection import create_db
from database.crud import add_demo_data
from ui.views import HomeView, DetailView

def main(page: ft.Page):
    page.title = "Instruction Manager v1.0"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 800
    page.window.height = 600

    create_db()
    add_demo_data()

    def route_change(route):
        page.views.clear()

        if page.route == "/":
            page.views.append(HomeView(page))
        elif page.route.startswith("/detail/"):
            inst_id = page.route.split("/")[-1]
            page.views.append(DetailView(page, inst_id))
        page.update()

    page.on_route_change = route_change

    route_change(None)

ft.run(main)