import flet as ft
import requests
from datetime import datetime, timezone, timedelta


API_KEY = '37e8603fe3dfb17b063de10f2beaba87'
HISTORY_FILE = "historyTrip.txt"


def main(page: ft.Page):
    page.title = 'Погодное приложение'
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 420
    page.window.height = 750
    page.window.resizable = False
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20


    def clear_page():
        page.controls.clear()

    def back_menu(e):
        show_menu()

    def section_title(text):
        return ft.Text(text, size=26, weight=ft.FontWeight.BOLD)

    def styled_button(text, on_click, icon=None):
        return ft.ElevatedButton(
            text,
            icon=icon,
            on_click=on_click,
            width=300,
            height=50,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
            ),
        )

    def unix_to_time(unix_ts, tz_offset_seconds):
        dt = datetime.fromtimestamp(unix_ts, tz=timezone.utc) + timedelta(seconds=tz_offset_seconds)
        return dt.strftime("%H:%M")


    def show_menu():
        clear_page()
        page.add(
            ft.Column(
                [
                    section_title("Погода App 🌤️"),
                    ft.Divider(),
                    styled_button('Посмотреть прогноз погоды', show_get_info, ft.Icons.WB_SUNNY),
                    styled_button('История поиска', show_history, ft.Icons.HISTORY),
                    styled_button('Настройки', show_change_theme, ft.Icons.SETTINGS),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            )
        )
        page.update()


    def show_get_info(e):
        clear_page()

        user_data = ft.TextField(
            label='Введите город',
            width=350,
            border_radius=10,
            autofocus=True,
        )

        loading = ft.ProgressRing(visible=False, width=28, height=28)
        error_text = ft.Text('', color=ft.Colors.RED_300)

        weather_icon = ft.Image(src="", width=100, height=100, visible=False)
        city_text = ft.Text('', size=22, weight=ft.FontWeight.BOLD)
        description_text = ft.Text('', size=16, italic=True)

        weather_card = ft.Container(
            visible=False,
            padding=20,
            border_radius=16,
            bgcolor=ft.Colors.with_opacity(0.06, ft.Colors.WHITE),
            content=ft.Column(
                [
                    ft.Row([weather_icon, ft.Column([city_text, description_text])],
                           alignment=ft.MainAxisAlignment.CENTER),
                    ft.Divider(),
                    ft.Row(
                        [
                            ft.Column([ft.Text("🌡 Темп.", size=12), ft.Text('', size=16, weight=ft.FontWeight.BOLD)]),
                            ft.Column([ft.Text("🤗 Ощущ.", size=12), ft.Text('', size=16, weight=ft.FontWeight.BOLD)]),
                            ft.Column([ft.Text("💨 Ветер", size=12), ft.Text('', size=16, weight=ft.FontWeight.BOLD)]),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                    ),
                    ft.Row(
                        [
                            ft.Column([ft.Text("💧 Влажн.", size=12), ft.Text('', size=16, weight=ft.FontWeight.BOLD)]),
                            ft.Column([ft.Text("📊 Давл.", size=12), ft.Text('', size=16, weight=ft.FontWeight.BOLD)]),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                    ),
                    ft.Row(
                        [
                            ft.Column([ft.Text("🌅 Восход", size=12), ft.Text('', size=16, weight=ft.FontWeight.BOLD)]),
                            ft.Column([ft.Text("🌇 Закат", size=12), ft.Text('', size=16, weight=ft.FontWeight.BOLD)]),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                    ),
                ],
                spacing=12,
            ),
        )

        temp_val = weather_card.content.controls[2].controls[0].controls[1]
        feels_val = weather_card.content.controls[2].controls[1].controls[1]
        wind_val = weather_card.content.controls[2].controls[2].controls[1]
        humidity_val = weather_card.content.controls[3].controls[0].controls[1]
        pressure_val = weather_card.content.controls[3].controls[1].controls[1]
        sunrise_val = weather_card.content.controls[4].controls[0].controls[1]
        sunset_val = weather_card.content.controls[4].controls[1].controls[1]

        def get_info(e):
            error_text.value = ''
            weather_card.visible = False
            weather_icon.visible = False

            city = user_data.value.strip()
            if len(city) < 1:
                return

            loading.visible = True
            page.update()

            try:
                url = (
                    f'https://api.openweathermap.org/data/2.5/weather'
                    f'?q={city}&appid={API_KEY}&units=metric&lang=ru'
                )
                res = requests.get(url, timeout=10).json()
            except requests.RequestException:
                loading.visible = False
                error_text.value = 'Ошибка сети. Проверьте подключение.'
                page.update()
                return

            loading.visible = False

            if res.get('cod') != 200:
                error_text.value = 'Город не найден'
                page.update()
                return

            temp = res['main']['temp']
            feels_like = res['main']['feels_like']
            wind = res['wind']['speed']
            humidity = res["main"]["humidity"]
            pressure = res["main"]["pressure"]
            description = res["weather"][0]["description"].capitalize()
            icon_code = res["weather"][0]["icon"]
            tz_offset = res.get("timezone", 0)
            sunrise = unix_to_time(res["sys"]["sunrise"], tz_offset)
            sunset = unix_to_time(res["sys"]["sunset"], tz_offset)

            weather_icon.src = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
            weather_icon.visible = True
            city_text.value = res.get("name", city)
            description_text.value = description

            temp_val.value = f"{temp:.1f} °C"
            feels_val.value = f"{feels_like:.1f} °C"
            wind_val.value = f"{wind} м/с"
            humidity_val.value = f"{humidity}%"
            pressure_val.value = f"{pressure} мм рт.ст."
            sunrise_val.value = sunrise
            sunset_val.value = sunset

            weather_card.visible = True
            page.update()

            history_line = (
                f"Город: {city}\n"
                f"Температура: {temp} °C (ощущается как {feels_like} °C)\n"
                f"Ветер: {wind} м/с | Влажность: {humidity}% | Давление: {pressure} мм рт.ст.\n"
                f"Восход: {sunrise} | Закат: {sunset}\n"
                f"Погода: {description}\n"
                f"-----------------------\n"
            )
            with open(HISTORY_FILE, "a", encoding="utf-8") as file:
                file.write(history_line)

        user_data.on_submit = get_info

        page.add(
            ft.Column(
                [
                    section_title('Погода App 🌤️'),
                    ft.Row([user_data], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row([loading], alignment=ft.MainAxisAlignment.CENTER),
                    error_text,
                    weather_card,
                    styled_button('Посмотреть прогноз', get_info, ft.Icons.SEARCH),
                    styled_button('Назад', back_menu, ft.Icons.ARROW_BACK),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
                scroll=ft.ScrollMode.AUTO,
            )
        )
        page.update()


    def show_history(e):
        clear_page()

        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as file:
                history = file.read()
            if not history.strip():
                history = "История поиска пуста"
        except FileNotFoundError:
            history = "История поиска пуста"

        page.add(
            ft.Column(
                [
                    section_title("История поиска"),
                    ft.Container(
                        padding=15,
                        border_radius=12,
                        bgcolor=ft.Colors.with_opacity(0.06, ft.Colors.WHITE),
                        content=ft.Text(history),
                        expand=True,
                    ),
                    styled_button("Назад", back_menu, ft.Icons.ARROW_BACK),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            )
        )
        page.update()

    def show_change_theme(e):
        clear_page()

        def change_theme(e):
            page.theme_mode = (
                ft.ThemeMode.LIGHT
                if page.theme_mode == ft.ThemeMode.DARK
                else ft.ThemeMode.DARK
            )
            theme_icon.icon = (
                ft.Icons.DARK_MODE
                if page.theme_mode == ft.ThemeMode.LIGHT
                else ft.Icons.LIGHT_MODE
            )
            page.update()

        theme_icon = ft.IconButton(
            icon=ft.Icons.LIGHT_MODE if page.theme_mode == ft.ThemeMode.DARK else ft.Icons.DARK_MODE,
            icon_size=32,
            on_click=change_theme,
        )

        page.add(
            ft.Column(
                [
                    section_title("Настройки"),
                    ft.Row([theme_icon], alignment=ft.MainAxisAlignment.CENTER),
                    styled_button('Назад', back_menu, ft.Icons.ARROW_BACK),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            )
        )
        page.update()

    show_menu()


ft.app(target=main)
