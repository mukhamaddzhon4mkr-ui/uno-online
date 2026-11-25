import tkinter as tk

from client import api
from client.ui_style import draw_gradient, round_rect, rotated_oval

WIDTH = 1000
HEIGHT = 620

BG_TOP = (0x12, 0x3A, 0x29)
BG_BOTTOM = (0x0C, 0x24, 0x19)

FIELD_BG = "#f4f6f8"
FIELD_BORDER = "#d5dde6"

GREEN = "#27ae60"
BLUE = "#2f5597"
RED = "#b42318"
GREY = "#7a8a9a"
INK = "#1f2a37"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("UNO Online")
        self.geometry(f"{WIDTH}x{HEIGHT}")
        self.resizable(False, False)
        self.configure(bg="#0c2419")

        self.canvas = tk.Canvas(self, width=WIDTH, height=HEIGHT, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        draw_gradient(self.canvas, WIDTH, HEIGHT, BG_TOP, BG_BOTTOM)

        self.widgets = []
        self.screen = "login"
        self.game_ids = {}

        self.bind("<Return>", self.on_enter)
        self.show_login()

    # Общее 

    def clear_screen(self):
        self.canvas.delete("screen")
        for widget in self.widgets:
            widget.destroy()
        self.widgets = []

    def add_widget(self, widget, **place):
        widget.place(**place)
        self.widgets.append(widget)

    def phone(self, text):
        return ("Segoe UI", text)

    def draw_logo(self):
        round_rect(self.canvas, 80, 130, 250, 350, 16, fill="#fbf8f1", outline="", tags="screen")
        round_rect(self.canvas, 86, 136, 244, 344, 12, fill="#d0342c", outline="", tags="screen")
        rotated_oval(self.canvas, 165, 240, 52, 78, -20, fill="#ffffff", outline="", tags="screen")
        self.canvas.create_text(165, 240, text="UNO", fill="#c0281f", font=("Segoe UI", 30, "bold"), angle=-20, tags="screen")
        self.canvas.create_text(80, 400, text="UNO Online", anchor="nw", fill="#ffffff", font=("Segoe UI", 32, "bold"), tags="screen")
        self.canvas.create_text(80, 452, text="игра по сети на двоих-четверых", anchor="nw", fill="#bcd8c8", font=("Segoe UI", 13), tags="screen")

    def canvas_button(self, x1, y1, x2, y2, text, fill, fg, tag, command, outline=""):
        round_rect(self.canvas, x1, y1, x2, y2, 10, fill=fill, outline=outline, width=1.5, tags=("screen", tag))
        self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=text, fill=fg, font=("Segoe UI", 12, "bold"), tags=("screen", tag))
        self.canvas.tag_bind(tag, "<Button-1>", command)

    def make_entry(self, x, y, show=None):
        entry = tk.Entry(self, font=("Segoe UI", 12), relief="flat", bg=FIELD_BG, highlightthickness=1, highlightbackground=FIELD_BORDER, highlightcolor=BLUE)
        if show is not None:
            entry.config(show=show)
        self.add_widget(entry, x=x, y=y, width=268, height=38)
        return entry

    # Экран входа 

    def show_login(self, event=None):
        self.clear_screen()
        self.screen = "login"

        self.draw_logo()
        round_rect(self.canvas, 520, 70, 880, 540, 18, fill="#ffffff", outline="", tags="screen")
        round_rect(self.canvas, 520, 70, 880, 86, 8, fill="#43b96a", outline="", tags="screen")
        self.canvas.create_rectangle(520, 80, 880, 86, fill="#43b96a", outline="", tags="screen")

        self.canvas.create_text(548, 110, text="Вход", anchor="nw", fill=INK, font=("Segoe UI", 24, "bold"), tags="screen")
        self.canvas.create_text(548, 152, text="Войди или создай новый аккаунт", anchor="nw", fill=GREY, font=("Segoe UI", 11), tags="screen")

        self.canvas.create_text(548, 190, text="Логин", anchor="nw", fill="#4a5a6a", font=("Segoe UI", 10, "bold"), tags="screen")
        self.username_entry = self.make_entry(548, 208)

        self.canvas.create_text(548, 264, text="Пароль", anchor="nw", fill="#4a5a6a", font=("Segoe UI", 10, "bold"), tags="screen")
        self.password_entry = self.make_entry(548, 282, show="*")

        # Глазик
        self.canvas.create_oval(822, 293, 846, 311, outline="#8a94a6", width=1.5, tags=("screen", "eye"))
        self.canvas.create_oval(828, 298, 840, 306, fill="#8a94a6", outline="", tags=("screen", "eye"))
        self.eye_line = self.canvas.create_line(820, 313, 848, 291, fill="#8a94a6", width=1.5, tags=("screen", "eye"))
        self.canvas.tag_bind("eye", "<Button-1>", self.toggle_password)

        self.error_item = self.canvas.create_text(548, 334, text="", anchor="nw", fill=RED, font=("Segoe UI", 10), tags="screen")

        self.canvas_button(548, 356, 852, 408, "Войти", GREEN, "#ffffff", "login_btn", self.do_login)
        self.canvas_button(548, 420, 852, 466, "Регистрация", "#ffffff", BLUE, "reg_btn", self.open_register, outline="#c9d3e3")

        self.username_entry.focus_set()

    def toggle_password(self, event=None):
        if self.password_entry.cget("show") == "*":
            self.password_entry.config(show="")
            self.canvas.itemconfig(self.eye_line, state="hidden")
        else:
            self.password_entry.config(show="*")
            self.canvas.itemconfig(self.eye_line, state="normal")

    def toggle_reg_password(self, event=None):
        if self.reg_password.cget("show") == "*":
            self.reg_password.config(show="")
            self.canvas.itemconfig(self.reg_eye1_line, state="hidden")
        else:
            self.reg_password.config(show="*")
            self.canvas.itemconfig(self.reg_eye1_line, state="normal")

    def toggle_reg_repeat(self, event=None):
        if self.reg_repeat.cget("show") == "*":
            self.reg_repeat.config(show="")
            self.canvas.itemconfig(self.reg_eye2_line, state="hidden")
        else:
            self.reg_repeat.config(show="*")
            self.canvas.itemconfig(self.reg_eye2_line, state="normal")
    
    def do_login(self, event=None):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            self.show_error("Заполни логин и пароль")
            return

        data, error = api.login(username, password)
        if error is not None:
            self.show_error(error)
            return

        self.show_lobby(data["username"])

    # экран регистрации 

    def open_register(self, event=None):
        self.clear_screen()
        self.screen = "register"

        self.draw_logo()
        round_rect(self.canvas, 520, 40, 880, 580, 18, fill="#ffffff", outline="", tags="screen")
        round_rect(self.canvas, 520, 40, 880, 56, 8, fill="#43b96a", outline="", tags="screen")
        self.canvas.create_rectangle(520, 50, 880, 56, fill="#43b96a", outline="", tags="screen")

        self.canvas.create_text(548, 78, text="Регистрация", anchor="nw", fill=INK, font=("Segoe UI", 22, "bold"), tags="screen")
        self.canvas.create_text(548, 118, text="Создай аккаунт для игры", anchor="nw", fill=GREY, font=("Segoe UI", 11), tags="screen")

        self.canvas.create_text(548, 156, text="Логин", anchor="nw", fill="#4a5a6a", font=("Segoe UI", 10, "bold"), tags="screen")
        self.reg_username = self.make_entry(548, 174)

        self.canvas.create_text(548, 230, text="Пароль", anchor="nw", fill="#4a5a6a", font=("Segoe UI", 10, "bold"), tags="screen")
        self.reg_password = self.make_entry(548, 248, show="*")

        self.canvas.create_text(548, 304, text="Повтори пароль", anchor="nw", fill="#4a5a6a", font=("Segoe UI", 10, "bold"), tags="screen")
        self.reg_repeat = self.make_entry(548, 322, show="*")

        self.canvas.create_oval(822, 259, 846, 277, outline="#8a94a6", width=1.5, tags=("screen", "reg_eye1"))
        self.canvas.create_oval(828, 264, 840, 272, fill="#8a94a6", outline="", tags=("screen", "reg_eye1"))
        self.reg_eye1_line = self.canvas.create_line(820, 279, 848, 257, fill="#8a94a6", width=1.5, tags=("screen", "reg_eye1"))
        self.canvas.tag_bind("reg_eye1", "<Button-1>", self.toggle_reg_password)

        self.canvas.create_oval(822, 333, 846, 351, outline="#8a94a6", width=1.5, tags=("screen", "reg_eye2"))
        self.canvas.create_oval(828, 338, 840, 346, fill="#8a94a6", outline="", tags=("screen", "reg_eye2"))
        self.reg_eye2_line = self.canvas.create_line(820, 353, 848, 331, fill="#8a94a6", width=1.5, tags=("screen", "reg_eye2"))
        self.canvas.tag_bind("reg_eye2", "<Button-1>", self.toggle_reg_repeat)

        self.error_item = self.canvas.create_text(548, 378, text="", anchor="nw", fill=RED, font=("Segoe UI", 10), tags="screen")

        self.canvas_button(548, 404, 852, 456, "Создать аккаунт", GREEN, "#ffffff", "create_btn", self.do_register)
        self.canvas_button(548, 468, 852, 514, "Назад", "#ffffff", BLUE, "back_btn", self.show_login, outline="#c9d3e3")

        self.reg_username.focus_set()

    def do_register(self, event=None):
        username = self.reg_username.get().strip()
        password = self.reg_password.get()
        repeat = self.reg_repeat.get()

        if len(username) < 2:
            self.show_error("Логин минимум 2 символа")
            return
        if len(password) < 4:
            self.show_error("Пароль минимум 4 символа")
            return
        if password != repeat:
            self.show_error("Пароли не совпадают")
            return

        data, error = api.register(username, password)
        if error is not None:
            self.show_error(error)
            return

        data, error = api.login(username, password)
        if error is not None:
            self.show_error(error)
            return

        self.show_lobby(data["username"])

    # Экран лобби 
    def show_lobby(self, username, event=None):
        self.clear_screen()
        self.screen = "lobby"
        self.username = username
        self.games_shown = []
        
        # Шапка
        self.canvas.create_rectangle(0, 0, WIDTH, 64, fill="#2c3e50", outline="", tags="screen")
        round_rect(self.canvas, 24, 14, 62, 50, 7, fill="#d0342c", outline="", tags="screen")
        self.canvas.create_text(43, 32, text="UNO", fill="#ffffff", font=("Segoe UI", 9, "bold"), tags="screen")
        self.canvas.create_text(78, 32, text="UNO Online", anchor="w", fill="#ffffff", font=("Segoe UI", 15, "bold"), tags="screen")
        self.canvas.create_text(930, 32, text=f"{username} · выйти", anchor="e", fill="#b9c6d6", font=("Segoe UI", 11), tags=("screen", "logout"))
        self.canvas.tag_bind("logout", "<Button-1>", self.do_logout)
        
        # Загаловок
        self.canvas.create_text(60, 96, text="Лобби", anchor="w", fill="#ffffff", font=("Segoe UI", 26, "bold"), tags="screen")
        self.count_item = self.canvas.create_text(180, 98, text="", anchor="w", fill="#8fe0a8", font=("Segoe UI", 11, "bold"), tags="screen")
        
        # Левая панель
        round_rect(self.canvas, 60, 136, 700, 556, 18, fill="#ffffff", outline="", tags="screen")
        self.canvas.create_text(84, 168, text="Открытые игры", anchor="nw", fill=INK, font=("Segoe UI", 16, "bold"), tags="screen")
        self.canvas.create_text(84, 196, text="Список обновляется кнопкой справа", anchor="nw", fill=GREY, font=("Segoe UI", 10), tags="screen")

        self.canvas.create_text(100, 228, text="Комната", anchor="nw", fill="#9aa9b8", font=("Segoe UI", 9, "bold"), tags="screen")
        self.canvas.create_text(184, 228, text="Хозяин", anchor="nw", fill="#9aa9b8", font=("Segoe UI", 9, "bold"), tags="screen")
        self.canvas.create_text(356, 228, text="Игроки", anchor="nw", fill="#9aa9b8",  font=("Segoe UI", 9, "bold"), tags="screen")
        self.canvas.create_text(446, 228, text="Статус", anchor="nw", fill="#9aa9b8", font=("Segoe UI", 9, "bold"), tags="screen")
        self.canvas.create_line(84, 244, 676, 244, fill="#e9eef4", tags="screen")

        # Правая панель
        round_rect(self.canvas, 720, 136, 940, 556, 18, fill="#ffffff", outline="", tags="screen")
        self.canvas.create_text(744, 168, text="Новая игра", anchor="nw", fill=INK, font=("Segoe UI", 14, "bold"), tags="screen")
        self.canvas_button(744, 196, 916, 248, "Создать игру", GREEN, "#ffffff", "create_game_btn", self.create_game)

        self.canvas.create_line(744, 270, 916, 270, fill="#e9eef4", tags="screen")

        self.canvas.create_text(744, 292, text="По коду комнаты", anchor="nw", fill="#4a5a6a",  font=("Segoe UI", 10, "bold"), tags="screen")
        self.code_entry = tk.Entry(self, font=("Segoe UI", 12), relief="flat", bg=FIELD_BG, highlightthickness=1, highlightbackground=FIELD_BORDER, highlightcolor=BLUE)
        self.add_widget(self.code_entry, x=744, y=310, width=172, height=36)

        self.canvas_button(744, 358, 916, 400, "Войти по коду", "#ffffff", BLUE, "join_code_btn", self.join_by_code, outline="#c9d3e3")
        self.canvas_button(744, 412, 916, 454, "Обновить список", "#ffffff", "#4a5a6a", "refresh_btn", self.refresh_games, outline="#c9d3e3")

        self.canvas.create_text(744, 486, text="Открытых игр:", anchor="nw", fill=GREY, font=("Segoe UI", 10), tags="screen")
        self.open_count_item = self.canvas.create_text(842, 486, text="0", anchor="nw", fill=INK, font=("Segoe UI", 10, "bold"), tags="screen")

        self.status_item = self.canvas.create_text(60, 582, text="", anchor="w", fill="#dfe8f2", font=("Segoe UI", 11),tags="screen")
        self.refresh_games()
        
    def draw_rooms(self, games):
        # Строки
        for i in range(4):
            self.canvas.delete(f"room{i}")

        self.games_shown = games[:4]

        for i in range(len(self.games_shown)):
            game = self.games_shown[i]
            y = 252 + i * 72
            tags = ("screen", f"room{i}")

            self.canvas.create_rectangle(84, y, 676, y + 64, fill="#fbfcfe" if i % 2 else "#ffffff", outline="#e6ecf3", tags=tags)

            round_rect(self.canvas, 100, y + 14, 168, y + 50, 8, fill="#1f2a37", outline="", tags=tags)
            self.canvas.create_text(134, y + 32, text=game["room_code"], fill="#ffffff", font=("Segoe UI", 11, "bold"), tags=tags)

            self.canvas.create_text(184, y + 22, text=game["host"], anchor="w", fill=INK, font=("Segoe UI", 11, "bold"), tags=tags)
            self.canvas.create_text(184, y + 42, text="хозяин комнаты", anchor="w", fill="#9aa9b8", font=("Segoe UI", 9), tags=tags)

            self.canvas.create_text(356, y + 22, text=f"{game['players']} из 4", anchor="w", fill="#4a5a6a", font=("Segoe UI", 9, "bold"), tags=tags)
            for d in range(4):
                color = "#2f8f45" if d < game["players"] else "#dfe6ee"
                self.canvas.create_oval(356 + d * 16, y + 40, 366 + d * 16, y + 50, fill=color, outline="", tags=tags)

            if game["status"] == "waiting":
                chip_text, chip_bg, chip_fg = "ждём", "#fff5d6", "#8a6100"
            else:
                chip_text, chip_bg, chip_fg = "идёт", "#eef1f5", "#667085"

            round_rect(self.canvas, 446, y + 18, 570, y + 46, 14, fill=chip_bg, outline="", tags=tags)
            self.canvas.create_text(508, y + 32, text=chip_text, fill=chip_fg, font=("Segoe UI", 10, "bold"), tags=tags)

            round_rect(self.canvas, 584, y + 14, 668, y + 50, 10, fill=GREEN, outline="", tags=tags + ("join_row",))
            self.canvas.create_text(626, y + 32, text="Войти", fill="#ffffff", font=("Segoe UI", 11, "bold"), tags=tags + ("join_row",))

        self.canvas.tag_bind("join_row", "<Button-1>", self.join_row)
        self.canvas.itemconfig(self.count_item, text=f"{len(games)} игры")
        self.canvas.itemconfig(self.open_count_item, text=str(len(games)))
        
    def refresh_games(self, event=None):
        games, error = api.list_games()
        if error is not None:
            self.show_status(error)
            return
        
        self.draw_rooms(games)
        self.show_status(f"Открытых игр: {len(games)}")
        
    def join_row(self, event=None):
        if event is None:
            return
        
        index = (event.y - 252) // 72
        if index < 0 or index >= len(self.games_shown):
            return
        
        game = self.games_shown[index]
        self.show_status(f"Комната {game['room_code']} выбрана стол появится дальше")
    
    def join_by_code(self, event=None):
        code = self.code_entry.get().strip().upper()
        
        if not code:
            self.show_status("Введите код комнаты")
            return
        
        games, error = api.list_games()
        if error is not None:
            self.show_status(error)
            return
        
        for game in games:
            if game["room_code"] == code:
                self.show_status(f"Комната {code} найдена, стол появится дальше")
                return
        
        self.show_status("Комната с таким кодом не найдена")
        
    def create_game(self, event=None):
        game, error = api.create_game()
        if error is not None:
            self.show_status(error)
            return
        
        self.refresh_games()
        self.show_status(f"Создана комната {game['room_code']}")
    
    def do_logout(self, event=None):
        api.logout()
        self.show_login()
        
    def show_status(self, text):
        self.canvas.itemconfig(self.status_item, text=text)
    
    def show_error(self, text):
        self.canvas.itemconfig(self.error_item, text=text)

    def on_enter(self, event):
        if self.screen == "login":
            self.do_login()
        elif self.screen == "register":
            self.do_register()
    
