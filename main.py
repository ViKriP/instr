import os

import django
import flet as ft
from dotenv import load_dotenv

# Загружаем .env файл
load_dotenv()

# Разрешить синхронные вызовы Django в асинхронном Flet
# (ОБЯЗАТЕЛЬНО true ДЛЯ DESKTOP)
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

# Настройка окружения для Django
# Указываем, где лежат настройки
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Инициализация Django
# В этот момент Django подключается к БД и загружает приложения
django.setup()

# Импорты UI (ОБЯЗАТЕЛЬНО ПОСЛЕ django.setup!)
# Если импортировать раньше, Python ругается, что модели не загружены
from core.logger import logger
from ui.edit_view import InstructionEditView
from ui.views import DetailView, HomeView


def main(page: ft.Page):
    logger.info("🚀 Приложение запускается...")
    page.title = "Instruction Manager v0.2"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 800
    page.window.height = 600

    def route_change(route):

        # если текущий маршрут уже отображен как верхний View, ничего не делаем
        if len(page.views) > 1 and page.views[-1].route == page.route:
            return

        # Маршрутизация
        if page.route == "/":
            page.views.clear()
            page.views.append(HomeView(page))
            logger.info("Главная страница загружена")
        elif page.route == "/create":
            page.views.append(InstructionEditView(page))
        elif page.route.startswith("/edit/"):
            try:
                inst_id = int(page.route.split("/")[-1])
                page.views.append(InstructionEditView(page, inst_id))
            except ValueError:
                page.go("/")
        elif page.route.startswith("/detail/"):
            inst_id = page.route.split("/")[-1]
            page.views.append(DetailView(page, inst_id))
            pass

        page.update()

    async def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        # page.go(top_view.route)
        await page.push_route(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    # page.go(page.route)
    # page.push_route(page.route)

    route_change("/")


def start_app():
    """
    Эта функция будет вызвана при вводе команды в терминал.
    Она просто запускает цикл Flet.
    """
    ft.run(main)


# Оставляем классический запуск для удобства разработки
if __name__ == "__main__":
    start_app()
