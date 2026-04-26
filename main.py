import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd

class AutoCatalogApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoExpert 2025")
        self.root.geometry("1200x800")
        
        self.is_fullscreen = False
        self.dark_mode = True 
        
        # Настройка палитр тем (темная и светлая)
        self.themes = {
            "dark": {
                "bg": "#0B0E14",
                "side": "#151921",
                "accent": "#7B61FF",
                "text": "#FFFFFF",
                "card": "#1C222D",
                "dim": "#5E67D4",
                "search_bg": "#252C3A"  },
            "light": {
                "bg": "#F0F2F5",
                "side": "#CFCFCF",
                "accent": "#004879",
                "text": "#2E2E2E",
                "card": "#D1D1D1",
                "dim": "#001F75",
                "search_bg": "#E4E6EB" }  }
        
        self.colors = self.themes["dark"]
        self.root.configure(bg=self.colors["bg"])

        try:
            # Загрузка базы данных
            self.df = pd.read_csv('Cars_Datasets_2025_RU_Final.csv', encoding='utf-8')
            self.df.columns = self.df.columns.str.strip()
            self.df = self.df.fillna("—")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Файл не найден: {e}")
            self.root.destroy()
            return

        self.setup_ui()
        
        # Горячие клавиши
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen_or_app)
        self.update_table(self.df)

    def set_theme(self, mode):
        # Переключение темы с сохранением поиска и выбранного авто
        # 1. Запоминаем текст поиска
        current_search = self.search_var.get()
        
        # 2. Запоминаем, какой автомобиль выбран сейчас
        selected_item = self.tree.selection()
        selected_index = selected_item[0] if selected_item else None
        
        self.dark_mode = (mode == "dark")
        self.colors = self.themes[mode]
        self.root.configure(bg=self.colors["bg"])
        
        if hasattr(self, 'menu_window'):
            self.menu_window.destroy()
            
        # 3. Полностью пересоздаем UI
        self.setup_ui()
        
        # 4. Восстанавливаем поиск
        self.search_var.set(current_search)
        self.filter_data() # Это заполнит таблицу данными
        
        # 5. Восстанавливаем выбор в таблице и карточку справа
        if selected_index and self.tree.exists(selected_index):
            self.tree.selection_set(selected_index)
            self.tree.see(selected_index)
            self.show_details(None)

    def show_menu(self):
        # Выпадающее меню под кнопкой три точки
        self.menu_window = tk.Toplevel(self.root)
        self.menu_window.overrideredirect(True)
        self.menu_window.configure(
            bg=self.colors["card"], 
            highlightbackground=self.colors["accent"], 
            highlightthickness=1 )
        
        # Расчет позиции меню
        x = self.menu_btn.winfo_rootx() - 120
        y = self.menu_btn.winfo_rooty() + 35
        self.menu_window.geometry(f"150x80+{x}+{y}")

        # Кнопки выбора темы
        tk.Button(
            self.menu_window, 
            text="Темная тема", 
            font=("Segoe UI", 10),
            bg=self.colors["card"], 
            fg=self.colors["text"], 
            bd=0, 
            activebackground=self.colors["accent"],
            padx=10, 
            anchor="w", 
            command=lambda: self.set_theme("dark")).pack(fill="x", ipady=5)
        
        tk.Button(
            self.menu_window, 
            text="Светлая тема", 
            font=("Segoe UI", 10),
            bg=self.colors["card"], 
            fg=self.colors["text"], 
            bd=0, 
            activebackground=self.colors["accent"],
            padx=10, 
            anchor="w", 
            command=lambda: self.set_theme("light")).pack(fill="x", ipady=5)

        # Закрытие при потере фокуса
        self.menu_window.bind("<FocusOut>", lambda e: self.menu_window.destroy())
        self.menu_window.focus_set()

    def setup_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # Левая панель
        sidebar = tk.Frame(self.root, bg=self.colors["side"], width=420)
        sidebar.pack(side="left", fill="both", padx=2, pady=2)
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar, 
            text="🚗 АВТОСПРАВОЧНИК", 
            font=("Segoe UI", 16, "bold"), 
            bg=self.colors["side"], 
            fg=self.colors["accent"] ).pack(pady=20)

        # Поиск
        search_frame = tk.Frame(sidebar, bg=self.colors["side"])
        search_frame.pack(fill="x", padx=20)
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_data)
        
        search_entry = tk.Entry(
            search_frame, 
            textvariable=self.search_var, 
            font=("Segoe UI", 11),
            bg=self.colors["search_bg"], 
            fg=self.colors["text"], 
            insertbackground=self.colors["text"], 
            borderwidth=0 )
        search_entry.pack(fill="x", pady=5, ipady=3)

        # Стиль таблицы и ползунка
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure(
            "Treeview", 
            background=self.colors["side"], 
            foreground=self.colors["text"], 
            fieldbackground=self.colors["side"], 
            rowheight=38, 
            borderwidth=0, 
            font=("Segoe UI Semibold", 12) )
        
        style.configure(
            "Treeview.Heading", 
            background=self.colors["search_bg"], 
            foreground=self.colors["text"], 
            borderwidth=1, 
            font=("Segoe UI Bold", 10) )
        
        style.map(
            "Treeview", 
            background=[('selected', self.colors["accent"])], 
            foreground=[('selected', 'white')] )
        
        style.configure(
            "Vertical.TScrollbar", 
            background=self.colors["accent"], 
            troughcolor=self.colors["side"], 
            borderwidth=0, 
            arrowsize=0,
            width=35
        )

        # Контейнер для таблицы
        tree_container = tk.Frame(sidebar, bg=self.colors["side"])
        tree_container.pack(fill="both", expand=True, padx=10, pady=20)
        
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        self.tree = ttk.Treeview(
            tree_container, 
            columns=("Brand", "Model"), 
            show="headings", 
            yscrollcommand=scrollbar.set  )
        scrollbar.config(command=self.tree.yview)
        
        self.tree.heading("Brand", text="МАРКА")
        self.tree.heading("Model", text="МОДЕЛЬ")
        self.tree.column("Brand", width=120)
        self.tree.column("Model", width=160)
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.show_details)

        # Правая часть
        self.content_container = tk.Frame(self.root, bg=self.colors["bg"])
        self.content_container.pack(side="right", fill="both", expand=True)

        # Кнопка меню в углу
        self.menu_btn = tk.Button(
            self.content_container, 
            text="⋮", 
            font=("Segoe UI", 20, "bold"),
            bg=self.colors["bg"], 
            fg=self.colors["text"], 
            bd=0, 
            activebackground=self.colors["bg"], 
            activeforeground=self.colors["accent"],
            cursor="hand2", 
            command=self.show_menu )
        self.menu_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-20, y=10)

        self.content = tk.Frame(self.content_container, bg=self.colors["bg"])
        self.content.place(relx=0.5, rely=0.5, anchor="center")

        self.placeholder = tk.Label(
            self.content, 
            text="Выберите модель из списка\nдля просмотра", 
            font=("Segoe UI", 16), 
            bg=self.colors["bg"], 
            fg=self.colors["dim"] )
        self.placeholder.pack()

        # Подсказка
        tk.Label(
            self.content_container, 
            text="F11 - Полноэкранный режим | Esc - Выход", 
            font=("Segoe UI", 8), 
            bg=self.colors["bg"], 
            fg=self.colors["dim"] ).place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

    def show_details(self, event):
        # Отображение карточки выбранного авто 
        selected = self.tree.selection()
        if not selected: 
            return
            
        car_idx = int(selected[0])
        car = self.df.loc[car_idx]
        
        for widget in self.content.winfo_children(): 
            widget.destroy()

        # Заголовки
        tk.Label(
            self.content, 
            text=str(car['Company Names']).upper(), 
            font=("Arial Black", 24), 
            bg=self.colors["bg"], 
            fg=self.colors["accent"] ).pack(pady=(0, 2))
        
        tk.Label(
            self.content, 
            text=car['Cars Names'], 
            font=("Impact", 48), 
            bg=self.colors["bg"], 
            fg=self.colors["text"] ).pack(pady=(0, 35))
        
        # Сетка данных (Карточки)
        grid_frame = tk.Frame(self.content, bg=self.colors["bg"])
        grid_frame.pack()
        
        specs = [
            ("💰 Стоимость", car['Cars Prices']), 
            ("⚙️ Двигатель", car['Engines']), 
            ("🐎 Мощность", car['HorsePower']), 
            ("⏱️ 0-100 км/ч", car['Performance(0 - 100 )KM/H']) ]

        for i, (lbl, val) in enumerate(specs):
            # Рамка карточки (для светлой темы добавляем обводку)
            card = tk.Frame(
                grid_frame, 
                bg=self.colors["card"], 
                padx=30, 
                pady=25, 
                width=300, 
                highlightbackground=self.colors["search_bg"] if not self.dark_mode else self.colors["bg"], 
                highlightthickness=1 )
            card.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="nsew")
            
            tk.Label(
                card, 
                text=lbl, 
                bg=self.colors["card"], 
                fg=self.colors["dim"], 
                font=("Segoe UI", 12) ).pack()
            
            tk.Label(
                card, 
                text=val, 
                bg=self.colors["card"], 
                fg=self.colors["text"], 
                font=("Segoe UI", 18, "bold") ).pack(pady=(5, 0))

    def update_table(self, data):
        self.tree.delete(*self.tree.get_children())
        for i, row in data.iterrows(): 
            self.tree.insert("", "end", iid=i, values=(row['Company Names'], row['Cars Names']))

    def filter_data(self, *args):
        val = self.search_var.get().lower()
        filtered = self.df[
            self.df['Cars Names'].str.lower().str.contains(val) | 
            self.df['Company Names'].str.lower().str.contains(val) ]
        self.update_table(filtered)

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)
        return "break"

    def exit_fullscreen_or_app(self, event=None):
        if self.is_fullscreen: 
            self.is_fullscreen = False
            self.root.attributes("-fullscreen", False)
        else: 
            self.root.destroy()
        return "break"

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoCatalogApp(root)
    root.mainloop()