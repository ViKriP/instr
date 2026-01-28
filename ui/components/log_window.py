import flet as ft

def build_log_dialog(page: ft.Page):
    """
    Создает и возвращает кортеж (dialog, log_view).
    Здесь находится вся настройка внешнего вида и кнопок.
    """
    
    # Сам список логов (визуальный элемент)
    log_view = ft.ListView(
        expand=True, 
        spacing=2, 
        padding=10, 
        auto_scroll=True,
    )

    # --- UI Обработчики ---
    
    async def copy_logs(e):
        # Собираем текст
        full_text = "\n".join([c.value for c in log_view.controls if isinstance(c, ft.Text)])
        if full_text:
            try:
                await page.clipboard.set(full_text)

                page.show_dialog(ft.SnackBar(
                    ft.Text("Скопировано!"), bgcolor=ft.Colors.GREEN_700)
                    )

                page.update()
            except Exception as ex:
                print(f"Ошибка буфера обмена: {ex}")

    def clear_logs(e):
        log_view.controls.clear()
        page.update()

    def close_dialog(e):
        dialog.open = False
        page.update()

    # --- Сборка Диалога ---
    
    dialog = ft.AlertDialog(
        title=ft.Text("Терминал выполнения"),
        content=ft.Container(
            content=log_view,
            bgcolor=ft.Colors.BLACK,
            border_radius=5,
            width=700,
            height=500,
        ),
        actions=[
            ft.IconButton(ft.Icons.COPY, tooltip="Копировать", on_click=copy_logs),
            ft.IconButton(ft.Icons.DELETE_SWEEP, tooltip="Очистить", icon_color=ft.Colors.RED_400, on_click=clear_logs),
            ft.TextButton("Закрыть", on_click=close_dialog),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    return dialog, log_view