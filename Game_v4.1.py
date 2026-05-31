import time
import os
import random
import json
import pygame
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
from pathlib import Path
import sys
import subprocess
import threading
import string
import platform


# ==================== ФИКС ДЛЯ EXE ====================
def is_frozen():
    return getattr(sys, 'frozen', False)


def setup_pygame():
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"

    if not is_frozen():
        try:
            import pygame
            return pygame
        except ImportError:
            print("Установка Pygame...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
                import pygame
                return pygame
            except Exception as e:
                print(f"Ошибка установки pygame: {e}")
                sys.exit(1)
    else:
        import pygame
        return pygame


pygame = setup_pygame()
import string
import platform
import random

# ==================== ФИКС ПУТЕЙ ДЛЯ РЕСУРСОВ ====================
def get_resource_path(relative_path):
    if is_frozen():
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# ==================== ЗАГРУЗКА МУЗЫКИ ====================
def load_music_files():
    music_directory_name = 'MUSIC'
    music_dir_path = Path(get_resource_path(music_directory_name))

    file_paths_by_name = {}
    extensions = ['.mp3', '.wav', '.flac', '.ogg', '.aac']

    if not is_frozen() and not music_dir_path.exists():
        music_dir_path.mkdir(exist_ok=True)
        return {}

    for ext in extensions:
        for file_path_object in music_dir_path.glob(f'*{ext}'):
            if file_path_object.is_file():
                filename = file_path_object.name
                full_path = file_path_object.resolve()
                file_paths_by_name[filename] = str(full_path)

    return file_paths_by_name


try:
    pygame.mixer.pre_init()
    pygame.mixer.init()
    pygame.init()
except Exception as e:
    print(f"Ошибка инициализации pygame: {e}")

music_files = load_music_files()


def get_music_file(filename, default_value=None):
    return music_files.get(filename, default_value)


# Загружаем файлы
FightMusic1 = get_music_file("DeathByGlamour.mp3") or get_music_file("Fight1.mp3")
FightMusic2 = get_music_file("JumpHimYay.mp3")
FightMusic3 = get_music_file("TheUltimaFight.mp3")
Casino = get_music_file("CASINO.mp3")
Garden = get_music_file("GARDEN.mp3")
Lose = get_music_file("LOSE.mp3")
Menu = get_music_file("MENU.mp3")
Shop = get_music_file("SHOP.mp3")
Start = get_music_file("START.mp3")
OhDangIt = get_music_file("OhDangIt.wav")
Select = get_music_file("SelectSound.mp3") or get_music_file("Select.mp3")
SaveTheGame = get_music_file("SaveTheGame.mp3")
ICantStopWin = get_music_file("ICantStopWin.mp3") or get_music_file("ICant.mp3")
IDK = get_music_file("IdkWhatPlayerDid.mp3") or get_music_file("Idk.mp3")
LetsGoGambling = get_music_file("LETSGOGAMBLING.wav")
PARRY = get_music_file("P.A.R.R.Y.mp3")
TRICKSTAB = get_music_file("TRICKSTAB.mp3")
DAMAGED = get_music_file("PlayerTakesDamage.mp3")
TAKEAWEAPON = get_music_file("WeaponTake.mp3")
DoDMG = get_music_file("DoDMG.mp3")
LAUGH = get_music_file("LAUGH.mp3")


class GameGUI:
    def __init__(self, root=None):
        if root is None:
            self.root = tk.Tk()
            self.is_new_window = True
        else:
            self.root = root
            self.is_new_window = False

        self.root.title("Ваше королевство")
        self.root.geometry("800x600")

        # Переменная для отслеживания процесса посадки
        self.planting_in_progress = False
        self.planting_thread = None

        # Инициализация игровых переменных
        self.reset_game_state()

        # Создание интерфейса
        self.create_widgets()

        if self.is_new_window:
            # Запуск музыки
            if Start:
                pygame.mixer.music.load(Start)
                pygame.mixer.music.play(-1)

            # Показываем начальное меню
            self.show_start_menu()
            self.root.mainloop()

    def reset_game_state(self):
        """Сброс всех игровых переменных"""
        self.gamername = ""
        self.talkfirst = "Королевство давно опустело без вас"
        self.playerpunchpower = 1
        self.playerpower = 1
        self.enemypunchpower = 1
        self.playermaxhp = 5
        self.enemymaxhp = 10
        self.playerhp = 5
        self.enemyhp = 2
        self.playerdefencestarter = 1
        self.playerdefence = 1
        self.money = 1
        self.menurestartermain = 1
        self.value = 0

        # Добавленные переменные
        self.parrychance = ["true", "false"]
        self.trickstabchance = ["true", "false", "false", "false"]
        self.parrytoken = 0
        self.playertotalhp = 5

        # Каталоги
        self.meleeitemcatalog = ["fighting_gloves", "fighting_gloves", "fighting_gloves", "fighting_gloves",
                                 "fighting_gloves", "fighting_gloves", "fighting_sword", "fighting_sword",
                                 "fighting_sword", "The_epic_sword"]
        self.armoritemscatalog = ["armorbasic", "armorbasic", "armorbasic", "armorbasic", "armorbasic", "armorbasic",
                                  "armorheavy", "armorheavy", "armorheavy", "thewarriorarmor"]
        self.spec_itemcatalog = ["The_happy_gnome", "+PARRY", "Trickstab_knife", "Old_Legendary_Amulet",
                                 "HealPotion", "HealthPotion", "PowerPotion"]
        self.seedsshopcatalog = ["Melon", "Melon", "Potato", "Potato", "Potato", "Potato", "Potato", "GoldenCarrot"]
        self.fightvars = ["punch", "enemyblock", "enemyidle"]
        self.shop_man_answer_got_money = ["Ну спасибо хехе", "Хоть кто-то купил это барахло",
                                          "Достойный покупатель хехе"]
        self.shop_man_answers_no_money = ["Я не беру в долг!", "Ага, а кто платить будет?", "Деньги вперед!",
                                          "Приходи когда заработаешь сколько нужно"]
        self.oldamulet_speedboost_dialog_catalog = ["Вы ощущаете что небесные светила движутся быстрее",
                                                    "Кажется, солнце движется быстрее чем раньше",
                                                    "Амулет загорелся зеленым светом..."]
        self.fightgamemusiccatalog = [FightMusic1, FightMusic2, FightMusic3]

        # Предметы
        self.item_gloves = 0
        self.item_sword = 0
        self.item_epicsword = 0
        self.item_basicarmor = 0
        self.item_armorheavy = 0
        self.item_warriorarmor = 0
        self.item_gnome = 0
        self.item_parry = 0
        self.item_trickstab = 0
        self.item_oldamulet = 0
        self.item_melonseeds = 0
        self.item_potatoseeds = 0
        self.item_gcarrotseeds = 0

        # Экипированные предметы
        self.glovesequiptoken = 0
        self.swordequiptoken = 0
        self.epicswordequiptoken = 0
        self.basicarmortoken = 0
        self.heavyarmortoken = 0
        self.elitearmortoken = 0
        self.amuletequiptoken = 0
        self.trickstabequiptoken = 0
        self.parryequiptoken = 0
        self.gnomeequiptoken = 0

        # Товары в магазине
        self.meleeitemsshop = random.choice(self.meleeitemcatalog)
        self.armoritemsshop = random.choice(self.armoritemscatalog)
        self.specitemshop = random.choice(self.spec_itemcatalog)
        self.seedsshop = random.choice(self.seedsshopcatalog)

        # Описания и цены предметов
        self.item_descriptions = {
            "fighting_gloves": "Перчатки для бокса. Оружие грубое, но для битв самое то (х2 атака)",
            "fighting_sword": "Меч. Оружие древнего воина. Сейчас правда устарело (х3 атака)",
            "The_epic_sword": "Легендарный меч героя. Легендарное оружие! Режет легко и быстро (х4 атака)",
            "armorbasic": "Плохонькая броня. Броня пажа. Да я стащил его с трупа ну и что? (х2 защита)",
            "armorheavy": "Тяжёлая броня. Элитная броня воина. Приобрел за большие деньги (х3 защита)",
            "thewarriorarmor": "Броня варвара. Об этом куске металла слагают легенды. (х4 защита)",
            "The_happy_gnome": "Дурно-гном. Этот гном проклят (сложный режим -4 атака -4 защита +10 к деньгам)",
            "+PARRY": "ПАРРИРОВАНИЕ. 'Thy end is now' (шанс контратаки 50/50)",
            "Trickstab_knife": "Удар в спину. 'Этот шпион уже прорвал нашу оборону' (шанс крит урона 2x)",
            "Old_Legendary_Amulet": "Старый Легендарный Амулет. Древний амулет силы (ускоряет рост растений)",
            "HealPotion": "Зелье лечения. Кто-то сварил эту бурду в странной лаборатории (лечит до максимума)",
            "HealthPotion": "Зелье здоровья. Эта вещь странным образом лечит (лечит до максимума)",
            "PowerPotion": "Зелье урона. Откуда люди узнали, что перекись мозгов гиены может тебя усилить?! (х2 атака)",
            "Melon": "Семена арбуза. Большая сладкая ягода (60 секунд, 30 монет)",
            "Potato": "Семена картошки. Картошка - вещь не привередливая (3 секунды, 3 монеты)",
            "GoldenCarrot": "Семена Золотой моркови. Это идеал во всем! (10 секунд, 20 монет)"
        }

        self.item_prices = {
            "fighting_gloves": 15,
            "fighting_sword": 30,
            "The_epic_sword": 100,
            "armorbasic": 30,
            "armorheavy": 45,
            "thewarriorarmor": 150,
            "The_happy_gnome": 100,
            "+PARRY": 70,
            "Trickstab_knife": 100,
            "Old_Legendary_Amulet": 50,
            "HealPotion": 25,
            "HealthPotion": 40,
            "PowerPotion": 40,
            "Melon": 100,
            "Potato": 125,
            "GoldenCarrot": 150
        }

    def create_widgets(self):
        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=70, height=25)
        self.text_area.pack(padx=10, pady=10)
        self.text_area.config(state=tk.DISABLED)

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(padx=10, pady=5)

        self.input_frame = tk.Frame(self.root)
        self.input_frame.pack(padx=10, pady=5, fill=tk.X)

        self.input_label = tk.Label(self.input_frame, text="Ввод вручную:")
        self.input_label.pack(side=tk.LEFT)

        self.input_entry = tk.Entry(self.input_frame, width=20)
        self.input_entry.pack(side=tk.LEFT, padx=5)
        self.input_entry.bind('<Return>', lambda event: self.process_input())

        self.submit_button = tk.Button(self.input_frame, text="Ввод", command=self.process_input)
        self.submit_button.pack(side=tk.LEFT)

        self.status_frame = tk.Frame(self.root)
        self.status_frame.pack(padx=10, pady=5, fill=tk.X)

        self.status_label = tk.Label(self.status_frame, text="", font=("Arial", 10, "bold"))
        self.status_label.pack()

    def show_start_menu(self):
        """Показывает начальное меню с выбором новой игры или загрузки"""
        if Menu:
            pygame.mixer.music.load(Start)
            pygame.mixer.music.play(-1)

        self.clear_text()
        self.clear_buttons()

        self.print_text("Добро пожаловать в Королевскую Игру!")
        self.print_text("\nВыберите действие:")

        tk.Button(self.button_frame, text="Новая игра", command=self.start_new_game, width=20).pack(pady=5)
        tk.Button(self.button_frame, text="Загрузить сохранение", command=self.load_game, width=20).pack(pady=5)
        tk.Button(self.button_frame, text="Выйти из игры", command=self.root.quit, width=20).pack(pady=5)

    def start_new_game(self):
        """Начинает новую игру с вводом имени"""
        if Select:
            pygame.mixer.Channel(0).play(pygame.mixer.Sound(Select), maxtime=600)

        # Сброс состояния
        self.reset_game_state()

        # Очистка интерфейса
        self.clear_text()
        self.clear_buttons()

        # Показ окна ввода имени
        self.show_name_input()

    def show_name_input(self):
        self.clear_buttons()
        self.print_text("Введите ваше имя Правитель:")

        name_window = tk.Toplevel(self.root)
        name_window.title("Ввод имени")
        name_window.geometry("300x150")
        name_window.transient(self.root)
        name_window.grab_set()

        tk.Label(name_window, text="Введите ваше имя:").pack(pady=10)
        name_entry = tk.Entry(name_window, width=30)
        name_entry.pack(pady=5)
        name_entry.focus_set()

        def submit_name():
            self.gamername = name_entry.get()
            if self.gamername:
                if Select:
                    pygame.mixer.Channel(0).play(pygame.mixer.Sound(Select), maxtime=600)
                name_window.destroy()
                self.show_main_menu()
            else:
                messagebox.showwarning("Внимание", "Введите имя!")

        tk.Button(name_window, text="Начать игру", command=submit_name).pack(pady=10)

        # Обработка закрытия окна
        def on_closing():
            if not self.gamername:
                self.gamername = "Игрок"
                name_window.destroy()
                self.show_main_menu()

        name_window.protocol("WM_DELETE_WINDOW", on_closing)

    def print_text(self, text):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, text + "\n")
        self.text_area.see(tk.END)
        self.text_area.config(state=tk.DISABLED)
        self.update_status()

    def clear_text(self):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        self.text_area.config(state=tk.DISABLED)

    def clear_buttons(self):
        for widget in self.button_frame.winfo_children():
            widget.destroy()

    def update_status(self):
        status_text = f"Игрок: {self.gamername} | Здоровье: {self.playerhp}/{self.playertotalhp} | Деньги: {self.money}💰 | Атака: {self.playerpower} | Защита: {self.playerdefence}"
        self.status_label.config(text=status_text)

    def process_input(self):
        user_input = self.input_entry.get()
        self.input_entry.delete(0, tk.END)
        if hasattr(self, 'current_handler'):
            self.current_handler(user_input)

    # ==================== ИСПРАВЛЕННАЯ ПОСАДКА ====================
    def start_garden(self):
        if Select:
            pygame.mixer.Channel(0).play(pygame.mixer.Sound(Select), maxtime=600)
        if Garden:
            pygame.mixer.music.load(Garden)
            pygame.mixer.music.play(-1)

        self.clear_text()
        self.clear_buttons()

        self.print_text("Хорошо правитель выберите культуру для посадки")

        options = [
            ("Пшеница (20 секунд) - 2💰", lambda: self.plant_crop_async(1, 2, 20, "Пшеница")),
            ("Помидоры (30 секунд) - 4💰", lambda: self.plant_crop_async(2, 4, 30, "Помидоры")),
            ("Овес (40 секунд) - 6💰", lambda: self.plant_crop_async(3, 6, 40, "Овес")),
            ("Арбуз (60 секунд) - 30💰", lambda: self.plant_crop_async(4, 30, 60, "Арбуз", seed_type="melon")),
            ("Картошка (3 секунды) - 3💰", lambda: self.plant_crop_async(5, 3, 3, "Картошка", seed_type="potato")),
            ("Золотая морковь (10 секунд) - 20💰",
             lambda: self.plant_crop_async(6, 20, 10, "Золотая морковь", seed_type="gcarrot")),
            ("Вернуться в меню", self.show_main_menu)
        ]

        for text, command in options:
            btn = tk.Button(self.button_frame, text=text, command=command, width=25)
            btn.pack(pady=2)

    def plant_crop_async(self, crop_type, reward, time_needed, crop_name, seed_type=None):
        """Асинхронная посадка культуры"""
        if self.planting_in_progress:
            self.print_text("Уже идет посадка другой культуры!")
            return

        if seed_type:
            if seed_type == "melon" and self.item_melonseeds <= 0:
                self.print_text("У вас нет семян арбуза!")
                return
            elif seed_type == "potato" and self.item_potatoseeds <= 0:
                self.print_text("У вас нет семян картошки!")
                return
            elif seed_type == "gcarrot" and self.item_gcarrotseeds <= 0:
                self.print_text("У вас нет семян золотой моркови!")
                return

        self.planting_in_progress = True
        self.clear_buttons()

        # Отображение прогресса
        self.print_text(f"Начата посадка {crop_name}...")

        # Запуск в отдельном потоке
        self.planting_thread = threading.Thread(
            target=self._plant_crop_thread,
            args=(crop_type, reward, time_needed, crop_name, seed_type),
            daemon=True
        )
        self.planting_thread.start()

        # Запуск обновления прогресса
        self._update_planting_progress(time_needed, crop_name)

    def _plant_crop_thread(self, crop_type, reward, time_needed, crop_name, seed_type):
        """Поток для посадки культуры"""
        original_time = time_needed

        # Проверка амулета
        if crop_type in [1, 2, 3] and self.item_oldamulet >= 1 and random.choice([True, False, False, False, False]):
            time_needed = time_needed // 10
            self.root.after(0, lambda: self.print_text(
                random.choice(self.oldamulet_speedboost_dialog_catalog)
            ))

        # Ожидание
        time.sleep(time_needed)

        # Возврат в основной поток для обновления GUI
        self.root.after(0, lambda: self._finish_planting(
            crop_name, reward, seed_type
        ))

    def _update_planting_progress(self, total_time, crop_name):
        """Обновление прогресса посадки"""
        if not self.planting_in_progress:
            return

        # Просто показываем, что идет процесс
        self.root.after(5000, lambda: self._show_planting_dots(crop_name))

    def _show_planting_dots(self, crop_name):
        """Показывает точки во время посадки"""
        if self.planting_in_progress:
            self.print_text(f"Выращиваем {crop_name}...")

    def _finish_planting(self, crop_name, reward, seed_type):
        """Завершение посадки"""
        self.print_text(f"{crop_name} выросла!")
        self.money += reward
        self.print_text(f"Вы получили {reward} золотых!")
        self.talkfirst = ""

        self.planting_in_progress = False

        # Кнопка для возврата
        self.clear_buttons()
        tk.Button(self.button_frame, text="Вернуться в меню",
                  command=self.show_main_menu).pack()

    def show_main_menu(self):
        if Menu:
            pygame.mixer.music.load(Menu)
            pygame.mixer.music.play(-1)

        self.clear_text()
        self.clear_buttons()

        self.print_text(f"Приветствуем вас {self.gamername}! {self.talkfirst}")
        self.print_text(f"На Вашем балансе {self.money}💰 золотых")
        self.print_text("\nВыберите чем Вы хотите заняться:")

        options = [
            ("Посадить урожай", self.start_garden),
            ("Напасть на врага", self.start_fight),
            ("Крутить казино", self.start_casino),
            ("Открыть магазин", self.start_shop),
            ("Открыть инвентарь", self.show_inventory),
            ("Сохранить игру", self.save_game),
            ("Загрузить сохранение", self.load_game_from_menu),
            ("В главное меню", self.show_start_menu)
        ]

        for text, command in options:
            btn = tk.Button(self.button_frame, text=text, command=command, width=20)
            btn.pack(pady=2)

    def new_game(self):
        """Начать новую игру из главного меню"""
        if Select:
            pygame.mixer.Channel(0).play(pygame.mixer.Sound(Select), maxtime=600)

        # Сброс состояния
        self.reset_game_state()

        # Очистка интерфейса
        self.clear_text()
        self.clear_buttons()

        # Показ окна ввода имени
        self.show_name_input()

    def load_game_from_menu(self):
        """Загрузить сохранение из главного меню"""
        if Select:
            pygame.mixer.Channel(0).play(pygame.mixer.Sound(Select), maxtime=600)
        self.load_game()

    def load_game(self):
        """Загрузить сохранение"""
        if Select:
            pygame.mixer.Channel(0).play(pygame.mixer.Sound(Select), maxtime=600)

        try:
            with open("GAMEDATA.json", "r") as f:
                loaded_data = json.load(f)

            # Загрузка всех переменных
            self.playerpunchpower = loaded_data.get("playerpunchpower", 1)
            self.enemypunchpower = loaded_data.get("enemypunchpower", 1)
            self.playermaxhp = loaded_data.get("playermaxhp", 5)
            self.enemymaxhp = loaded_data.get("enemymaxhp", 10)
            self.playerhp = loaded_data.get("playerhp", 5)
            self.enemyhp = loaded_data.get("enemyhp", 2)
            self.money = loaded_data.get("money", 1)
            self.menurestartermain = loaded_data.get("menurestartermain", 1)
            self.value = loaded_data.get("value", 0)

            # Предметы
            self.item_gloves = loaded_data.get("item_gloves", 0)
            self.item_sword = loaded_data.get("item_sword", 0)
            self.item_epicsword = loaded_data.get("item_epicsword", 0)
            self.item_basicarmor = loaded_data.get("item_basicarmor", 0)
            self.item_armorheavy = loaded_data.get("item_armorheavy", 0)
            self.item_warriorarmor = loaded_data.get("item_warriorarmor", 0)
            self.item_gnome = loaded_data.get("item_gnome", 0)
            self.item_parry = loaded_data.get("item_parry", 0)
            self.item_trickstab = loaded_data.get("item_trickstab", 0)
            self.item_oldamulet = loaded_data.get("item_oldamulet", 0)
            self.item_melonseeds = loaded_data.get("item_melonseeds", 0)
            self.item_potatoseeds = loaded_data.get("item_potatoseeds", 0)
            self.item_gcarrotseeds = loaded_data.get("item_gcarrotseeds", 0)

            self.gamername = loaded_data.get("gamername", "Игрок")

            # Экипировка
            self.glovesequiptoken = loaded_data.get("glovesequiptoken", 0)
            self.swordequiptoken = loaded_data.get("swordequiptoken", 0)
            self.epicswordequiptoken = loaded_data.get("epicswordequiptoken", 0)
            self.basicarmortoken = loaded_data.get("basicarmortoken", 0)
            self.heavyarmortoken = loaded_data.get("heavyarmortoken", 0)
            self.elitearmortoken = loaded_data.get("elitearmortoken", 0)
            self.amuletequiptoken = loaded_data.get("amuletequiptoken", 0)
            self.trickstabequiptoken = loaded_data.get("trickstabequiptoken", 0)
            self.parryequiptoken = loaded_data.get("parryequiptoken", 0)
            self.gnomeequiptoken = loaded_data.get("gnomeequiptoken", 0)

            # Магазин
            self.meleeitemsshop = loaded_data.get("meleeitemsshop", random.choice(self.meleeitemcatalog))
            self.armoritemsshop = loaded_data.get("armoritemsshop", random.choice(self.armoritemscatalog))
            self.specitemshop = loaded_data.get("specitemshop", random.choice(self.spec_itemcatalog))
            self.seedsshop = loaded_data.get("seedsshop", random.choice(self.seedsshopcatalog))

            # Применение экипировки
            self._apply_equipment_effects()

            if SaveTheGame:
                pygame.mixer.Channel(0).play(pygame.mixer.Sound(SaveTheGame))

            self.clear_text()
            self.print_text(f"Добро пожаловать обратно, {self.gamername}!")
            self.print_text("Игра успешно загружена!")
            time.sleep(1)
            self.show_main_menu()

        except FileNotFoundError:
            self.print_text("Сохранение не найдено!")
            messagebox.showinfo("Сохранение", "Сохранение не найдено. Начните новую игру.")
            self.show_main_menu()
        except Exception as e:
            self.print_text(f"Ошибка при загрузке: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось загрузить сохранение: {str(e)}")
            self.show_main_menu()

    def _apply_equipment_effects(self):
        """Применение эффектов экипировки"""
        # Оружие
        if self.glovesequiptoken:
            self.playerpower = self.playerpunchpower * 2
        elif self.swordequiptoken:
            self.playerpower = self.playerpunchpower * 3
        elif self.epicswordequiptoken:
            self.playerpower = self.playerpunchpower * 4
        else:
            self.playerpower = self.playerpunchpower

        # Броня
        if self.basicarmortoken:
            self.playertotalhp = self.playermaxhp * 2
            self.playerdefence = self.playerdefencestarter
        elif self.heavyarmortoken:
            self.playertotalhp = self.playermaxhp * 3
            self.playerdefence = self.playerdefencestarter * 2
        elif self.elitearmortoken:
            self.playertotalhp = self.playermaxhp * 4
            self.playerdefence = self.playerdefencestarter * 3
        else:
            self.playertotalhp = self.playermaxhp
            self.playerdefence = self.playerdefencestarter

        # Спецпредметы
        if self.gnomeequiptoken:
            self.playerdefence -= 4
            self.playerpower -= 4

    def save_game(self):
        if Select:
            pygame.mixer.Channel(0).play(pygame.mixer.Sound(Select), maxtime=600)

        self.clear_text()
        self.print_text("Сохранение игры...")

        data = {
            "playerpunchpower": self.playerpunchpower,
            "enemypunchpower": self.enemypunchpower,
            "playermaxhp": self.playermaxhp,
            "enemymaxhp": self.enemymaxhp,
            "playerhp": self.playerhp,
            "enemyhp": self.enemyhp,
            "money": self.money,
            "menurestartermain": self.menurestartermain,
            "value": self.value,
            "item_gloves": self.item_gloves,
            "item_sword": self.item_sword,
            "item_epicsword": self.item_epicsword,
            "item_basicarmor": self.item_basicarmor,
            "item_armorheavy": self.item_armorheavy,
            "item_warriorarmor": self.item_warriorarmor,
            "item_gnome": self.item_gnome,
            "item_parry": self.item_parry,
            "item_trickstab": self.item_trickstab,
            "item_oldamulet": self.item_oldamulet,
            "item_melonseeds": self.item_melonseeds,
            "item_potatoseeds": self.item_potatoseeds,
            "item_gcarrotseeds": self.item_gcarrotseeds,
            "gamername": self.gamername,
            "glovesequiptoken": self.glovesequiptoken,
            "swordequiptoken": self.swordequiptoken,
            "epicswordequiptoken": self.epicswordequiptoken,
            "basicarmortoken": self.basicarmortoken,
            "heavyarmortoken": self.heavyarmortoken,
            "elitearmortoken": self.elitearmortoken,
            "amuletequiptoken": self.amuletequiptoken,
            "trickstabequiptoken": self.trickstabequiptoken,
            "parryequiptoken": self.parryequiptoken,
            "gnomeequiptoken": self.gnomeequiptoken,
            "meleeitemsshop": self.meleeitemsshop,
            "armoritemsshop": self.armoritemsshop,
            "specitemshop": self.specitemshop,
            "seedsshop": self.seedsshop,
            "playertotalhp": self.playertotalhp,
            "playerdefencestarter": self.playerdefencestarter,
        }

        try:
            with open("GAMEDATA.json", "w", encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            if SaveTheGame:
                pygame.mixer.Channel(0).play(pygame.mixer.Sound(SaveTheGame))
            self.print_text("Данные игры успешно сохранены!")
        except Exception as e:
            self.print_text(f"Ошибка при сохранении: {e}")

        self.clear_buttons()
        tk.Button(self.button_frame, text="Вернуться в меню", command=self.show_main_menu).pack()

    def start_fight(self):
        if self.fightgamemusiccatalog:
            FightMusicChoice = random.choice(self.fightgamemusiccatalog)
            pygame.mixer.music.load(FightMusicChoice)
            pygame.mixer.music.play(-1)

        # Настройка врага
        if self.playerpower >= 35:
            self.enemyhp = random.choice([40, 100])
            self.enemypunchpower = random.choice([10, 15])
        elif self.playerpower >= 15:
            self.enemyhp = random.choice([15, 40])
            self.enemypunchpower = random.choice([5, 10])
        else:
            self.enemyhp = random.choice([3, 15])
            self.enemypunchpower = random.choice([1, 2])

        self.clear_text()
        self.clear_buttons()

        self.print_text(f"Враг перед вами!")
        self.print_text(f"Его здоровье: {self.enemyhp}")
        self.print_text(f"Ваше здоровье: {self.playerhp}")
        self.print_text("\nВыберите действие:")

        tk.Button(self.button_frame, text="Ударить", command=lambda: self.fight_action(1)).pack(side=tk.LEFT, padx=5)
        tk.Button(self.button_frame, text="Блок", command=lambda: self.fight_action(2)).pack(side=tk.LEFT, padx=5)

    def fight_action(self, choice):
        fightenemychoice = random.choice(self.fightvars)

        if choice == 1:  # Удар
            if fightenemychoice == "punch":
                if self.trickstabequiptoken >= 1:
                    trickstabsuccess = random.choice(self.trickstabchance)
                    if trickstabsuccess == "true":
                        if TRICKSTAB:
                            pygame.mixer.Channel(0).play(pygame.mixer.Sound(TRICKSTAB), maxtime=600)
                        damage_to_player = max(0, self.enemypunchpower - self.playerdefence)
                        self.playerhp -= damage_to_player
                        self.enemyhp -= self.playerpower * 2
                        self.print_text("Вы сделали удар в спину! Крит урон!")
                    else:
                        if DoDMG:
                            pygame.mixer.Channel(0).play(pygame.mixer.Sound(DoDMG))
                        damage_to_player = max(0, self.enemypunchpower - self.playerdefence)
                        self.playerhp -= damage_to_player
                        self.enemyhp -= self.playerpower
                        self.print_text("Вы ударили друг друга!")
                else:
                    if DoDMG:
                        pygame.mixer.Channel(0).play(pygame.mixer.Sound(DoDMG))
                    damage_to_player = max(0, self.enemypunchpower - self.playerdefence)
                    self.playerhp -= damage_to_player
                    self.enemyhp -= self.playerpower
                    self.print_text("Вы ударили друг друга!")

            elif fightenemychoice == "enemyblock":
                if DAMAGED:
                    pygame.mixer.Channel(0).play(pygame.mixer.Sound(DAMAGED))
                damage_to_player = max(0, self.enemypunchpower - self.playerdefence)
                self.playerhp -= damage_to_player
                self.print_text("Враг парировал вашу атаку")
            else:  # enemyidle
                self.enemyhp -= self.playerpower
                self.print_text("Враг просто стоял и вы его ударили!")

        elif choice == 2:  # Блок
            if fightenemychoice == "punch":
                self.print_text("Вы парировали атаку врага!")

                if self.parryequiptoken == 1:
                    parryifwork = random.choice(self.parrychance)
                    if parryifwork == "true":
                        if PARRY:
                            pygame.mixer.Channel(0).play(pygame.mixer.Sound(PARRY), maxtime=600)
                        self.enemyhp -= self.playerpower * 3
                        self.print_text("Вы сделали контратаку с тройным уроном!")
                        self.parrytoken = 0
                    elif parryifwork == "false":
                        self.parrytoken = 1
                        self.print_text("Вы готовы к следующей контратаке!")
                elif self.parrytoken >= 1:
                    if PARRY:
                        pygame.mixer.Channel(0).play(pygame.mixer.Sound(PARRY), maxtime=600)
                    self.enemyhp -= self.playerpower * 2
                    self.print_text("Вы сделали контратаку с двойным уроном!")
                    self.parrytoken = 0
                else:
                    if DoDMG:
                        pygame.mixer.Channel(0).play(pygame.mixer.Sound(DoDMG))
                    self.enemyhp -= self.playerpower

            elif fightenemychoice == "enemyblock":
                damage_to_player = max(0, self.enemypunchpower - self.playerdefence)
                self.playerhp -= damage_to_player
                self.print_text("Враг заблокировался и вы тоже... но его кулак был быстрее")
            else:  # enemyidle
                if LAUGH:
                    pygame.mixer.Channel(0).play(pygame.mixer.Sound(LAUGH))
                self.enemyhp -= self.playerpower
                self.print_text("Враг просто стоял и смотрел как вы блокировали!")

        self.print_text(f"\nРезультат раунда:")
        self.print_text(f"Ваше здоровье: {self.playerhp}")
        self.print_text(f"Здоровье врага: {self.enemyhp}")

        # Проверка конца боя
        if self.playerhp <= 0:
            self.print_text("\nВы проиграли😭")
            self.money = max(0, self.money - 3)
            self.print_text("Враг забрал 3 золотых")
            self.talkfirst = ""

            if self.playertotalhp >= 35:
                self.playerhp = 37
            elif self.playertotalhp >= 15:
                self.playerhp = 17
            else:
                self.playerhp = 3

            self.clear_buttons()
            tk.Button(self.button_frame, text="Вернуться в меню", command=self.show_main_menu).pack()

        elif self.enemyhp <= 0:
            moneygain = random.randint(1, 10)

            if self.gnomeequiptoken >= 1:
                moneygain += 10
                self.print_text("ГнОм Пр3нно7ит бо7атсв0...")
                self.playerdefence += 4
                self.playerpower += 4

            self.money += moneygain
            self.print_text(f"\nВы победили!")
            self.print_text(f"Вы забрали у врага {moneygain} золотых")
            self.talkfirst = ""

            self.clear_buttons()
            tk.Button(self.button_frame, text="Вернуться в меню", command=self.show_main_menu).pack()

        else:
            self.print_text("\nВыберите следующее действие:")

    def start_casino(self):
        if Select:
            pygame.mixer.Channel(0).play(pygame.mixer.Sound(Select), maxtime=600)
        if Casino:
            pygame.mixer.music.load(Casino)
            pygame.mixer.music.play(-1)

        self.clear_text()
        self.clear_buttons()

        self.print_text("Добро пожаловать в казино!")
        self.print_text(f"Ваш баланс: {self.money}💰")
        self.print_text("\nВыберите игру:")

        tk.Button(self.button_frame, text="Красное/Чёрное", command=self.casino_red_black).pack(pady=2)
        tk.Button(self.button_frame, text="Угадай число", command=self.casino_numbers).pack(pady=2)
        tk.Button(self.button_frame, text="Найди файл", command=self.casino_filefinder).pack(pady=2)
        tk.Button(self.button_frame, text="Вернуться в меню", command=self.show_main_menu).pack(pady=2)

    def casino_red_black(self):
        self.clear_buttons()
        self.print_text("\nВыберите ставку (от 10 до 29) или 0 для отмены:")
        self.current_handler = self.process_casino_bet

    def process_casino_bet(self, bet_str):
        try:
            bet = float(bet_str)

            if bet == 0:
                self.show_main_menu()
                return

            if bet < 10 or bet > 29:
                self.print_text("Ставка должна быть от 10 до 29!")
                return

            if bet > self.money:
                self.print_text("У вас недостаточно денег!")
                return

            self.value = bet
            self.clear_buttons()
            self.print_text(f"\nСтавка {bet} принята. Выберите:")

            tk.Button(self.button_frame, text="Красное", command=lambda: self.play_red_black("red")).pack(side=tk.LEFT,
                                                                                                          padx=5)
            tk.Button(self.button_frame, text="Чёрное", command=lambda: self.play_red_black("black")).pack(side=tk.LEFT,
                                                                                                           padx=5)

        except ValueError:
            self.print_text("Пожалуйста, введите число!")

    def play_red_black(self, player_choice):
        self.print_text("Крутим барабан...")
        if LetsGoGambling:
            pygame.mixer.Channel(0).play(pygame.mixer.Sound(LetsGoGambling))
        time.sleep(3.557)

        result = random.choice(["red", "black"])
        self.print_text(f"Выпало: {'Красное' if result == 'red' else 'Чёрное'}")

        if (player_choice == "red" and result == "red") or (player_choice == "black" and result == "black"):
            self.money += self.value
            if ICantStopWin:
                pygame.mixer.Channel(0).play(pygame.mixer.Sound(ICantStopWin))
            self.print_text(f"Вы победили! +{self.value}💰")
        else:
            self.money -= self.value
            if OhDangIt:
                pygame.mixer.Channel(0).play(pygame.mixer.Sound(OhDangIt))
            self.print_text(f"Вы проиграли! -{self.value}💰")

        self.clear_buttons()
        tk.Button(self.button_frame, text="Сыграть ещё", command=self.start_casino).pack(side=tk.LEFT, padx=5)
        tk.Button(self.button_frame, text="Вернуться в меню", command=self.show_main_menu).pack(side=tk.LEFT, padx=5)

    def casino_numbers(self):
        self.clear_buttons()
        self.print_text("\nВыберите сложность:")

        tk.Button(self.button_frame, text="Легко (1-5, х1)", command=lambda: self.play_numbers(5, 1)).pack(pady=2)
        tk.Button(self.button_frame, text="Средне (1-10, х2)", command=lambda: self.play_numbers(10, 2)).pack(pady=2)
        tk.Button(self.button_frame, text="Сложно (1-20, х5)", command=lambda: self.play_numbers(20, 5)).pack(pady=2)
        tk.Button(self.button_frame, text="Назад", command=self.start_casino).pack(pady=2)

    def play_numbers(self, max_num, multiplier):
        self.print_text(f"\nВведите ставку (от 10 до 29) или 0 для отмены:")
        self.current_handler = lambda bet_str: self.process_numbers_bet(bet_str, max_num, multiplier)

    def process_numbers_bet(self, bet_str, max_num, multiplier):
        try:
            bet = float(bet_str)

            if bet == 0:
                self.start_casino()
                return

            if bet < 10 or bet > 29:
                self.print_text("Ставка должна быть от 10 до 29!")
                return

            if bet > self.money:
                self.print_text("У вас недостаточно денег!")
                return

            self.value = bet * multiplier
            self.clear_buttons()

            # Создаем кнопки с числами
            self.print_text(f"\nВыберите число от 1 до {max_num}:")

            for i in range(1, max_num + 1):
                if i <= 10:  # Показываем первые 10 кнопок в первом ряду
                    btn = tk.Button(self.button_frame, text=str(i),
                                    command=lambda num=i: self.check_number(num, max_num))
                    btn.pack(side=tk.LEFT, padx=2)

            if max_num > 10:  # Второй ряд для остальных чисел
                second_row = tk.Frame(self.button_frame)
                second_row.pack()
                for i in range(11, max_num + 1):
                    btn = tk.Button(second_row, text=str(i),
                                    command=lambda num=i: self.check_number(num, max_num))
                    btn.pack(side=tk.LEFT, padx=2)

        except ValueError:
            self.print_text("Пожалуйста, введите число!")

    def check_number(self, player_num, max_num):
        winning_num = random.randint(1, max_num)
        self.print_text(f"\nВы выбрали: {player_num}")
        self.print_text(f"Выпало число: {winning_num}")

        if player_num == winning_num:
            self.money += self.value
            if ICantStopWin:
                pygame.mixer.Channel(0).play(pygame.mixer.Sound(ICantStopWin))
            self.print_text(f"Вы победили! +{self.value}💰")
        else:
            self.money -= self.value
            if OhDangIt:
                pygame.mixer.Channel(0).play(pygame.mixer.Sound(OhDangIt))
            self.print_text(f"Вы проиграли! -{self.value}💰")

        self.clear_buttons()
        tk.Button(self.button_frame, text="Сыграть ещё", command=self.start_casino).pack(side=tk.LEFT, padx=5)
        tk.Button(self.button_frame, text="Вернуться в меню", command=self.show_main_menu).pack(side=tk.LEFT, padx=5)

    def casino_filefinder(self):
        """Игра 'Найди файл'"""
        if Select:
            pygame.mixer.Channel(0).play(pygame.mixer.Sound(Select), maxtime=600)

        self.clear_text()
        self.clear_buttons()

        self.print_text("Игра 'Найди файл'!")
        self.print_text(f"Ваш баланс: {self.money}💰")
        self.print_text("\nЯ создал секретный файл где-то на вашем компьютере.")
        self.print_text("Ваша задача - угадать его имя.")

        self.print_text("\nВведите ставку (от 10 до 29) или 0 для отмены:")
        self.current_handler = self.process_filefinder_bet

    def process_filefinder_bet(self, bet_str):
        try:
            # Очищаем ввод от пробелов
            bet_str = bet_str.strip()

            # Проверяем, что ввод не пустой
            if not bet_str:
                self.print_text("Пожалуйста, введите ставку!")
                return

            bet = float(bet_str)

            if bet == 0:
                self.start_casino()
                return

            if bet < 10 or bet > 29:
                self.print_text("Ставка должна быть от 10 до 29!")
                return

            if bet > self.money:
                self.print_text("У вас недостаточно денег!")
                return


        except ValueError:
            self.print_text("Пожалуйста, введите корректное число!")
        self.value = bet
        self.play_filefinder_game()

    def play_filefinder_game(self):

        self.clear_text()
        self.clear_buttons()

        self.print_text("Создаю секретный файл где-то на вашем компьютере...")

        try:
            # Определяем операционную систему
            system = platform.system()

            # Выбираем корневой диск/директорию
            if system == "Windows":
                drives = ['C:\\', 'D:\\', 'E:\\', 'F:\\']
                existing_drives = [d for d in drives if os.path.exists(d)]
                if not existing_drives:
                    existing_drives = ['C:\\']
                root_dir = random.choice(existing_drives)

                # Создаем более сложный путь с несколькими уровнями
                path_components = []

                # Первый уровень (основные папки)
                common_dirs = ['Users', 'Program Files', 'Windows', 'Temp', 'ProgramData',
                               'PerfLogs', 'Intel', 'AMD', 'NVIDIA', 'Program Files (x86)']
                existing_dirs = [d for d in common_dirs if os.path.exists(os.path.join(root_dir, d))]
                if existing_dirs:
                    path_components.append(random.choice(existing_dirs))

                # Второй уровень (случайные подпапки или реальные)
                if random.choice([True, False]):
                    # Создаем случайные папки
                    for _ in range(random.randint(1, 3)):
                        folder_name = ''.join(random.choices(string.ascii_lowercase, k=random.randint(4, 10)))
                        path_components.append(folder_name)
                else:
                    # Или используем реальные подпапки
                    if path_components and os.path.exists(os.path.join(root_dir, *path_components)):
                        try:
                            subdirs = [d for d in os.listdir(os.path.join(root_dir, *path_components))
                                       if os.path.isdir(os.path.join(root_dir, *path_components, d))]
                            if subdirs:
                                path_components.append(random.choice(subdirs))
                        except:
                            pass

            elif system == "Darwin":  # macOS
                root_dir = '/'
                path_components = []

                common_dirs = ['Users', 'Applications', 'Library', 'System', 'private', 'tmp',
                               'Volumes', 'opt', 'usr', 'var']
                existing_dirs = [d for d in common_dirs if os.path.exists(os.path.join(root_dir, d))]
                if existing_dirs:
                    path_components.append(random.choice(existing_dirs))

            else:  # Linux/Unix
                root_dir = '/'
                path_components = []

                common_dirs = ['home', 'etc', 'var', 'tmp', 'usr', 'opt', 'mnt', 'media',
                               'bin', 'sbin', 'lib', 'root']
                existing_dirs = [d for d in common_dirs if os.path.exists(os.path.join(root_dir, d))]
                if existing_dirs:
                    path_components.append(random.choice(existing_dirs))

            # Создаем полный путь к директории
            current_dir = root_dir
            for comp in path_components:
                current_dir = os.path.join(current_dir, comp)

            # Создаем директорию, если не существует
            os.makedirs(current_dir, exist_ok=True)

            # Создаем уникальное имя файла
            self.secret_filename = ''.join(random.choices(
                string.ascii_lowercase + string.digits, k=12
            ))
            file_extension = random.choice(['.txt', '.tmp', '.dat', '.log'])
            full_filename = self.secret_filename + file_extension
            filepath = os.path.join(current_dir, full_filename)

            # Создаем файл с содержимым
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Секретный файл игры Королевство\n")
                f.write(f"ID: {self.secret_filename}\n")
                f.write(f"Создан: {time.ctime()}\n")
                f.write(f"Удачи в поиске!\n")

            self.secret_file_fullpath = filepath

            # Генерируем подсказки
            self.generate_file_hints(root_dir, current_dir, system)

            # Запрашиваем у пользователя имя файла
            self.print_text("\n" + "=" * 50)
            self.print_text("Файл успешно создан в системе!")
            self.print_text(f"Имя файла: ???{file_extension}")
            self.print_text("\nПодсказки для поиска:")

            for i, hint in enumerate(self.file_hints, 1):
                self.print_text(f"  {i}. {hint}")

            self.print_text("\nВведите полное имя файла (с расширением):")
            self.current_handler = self.check_file_guess

        except PermissionError:
            self.print_text("❌ Ошибка доступа! Нет прав для создания файла.")
            self.print_text("Попробуйте запустить игру от имени администратора.")
            self.start_casino()
        except Exception as e:
            self.print_text(f"❌ Ошибка при создании файла: {str(e)}")
            self.start_casino()

    def generate_file_hints(self, root_dir, actual_dir, system):
        """Генерирует подсказки для поиска файла"""
        self.file_hints = []

        # Первая подсказка - реальный путь (но не полный)
        if system == "Windows":
            # Показываем диск и первую папку
            hint = f"Находится на диске {root_dir[0]}"
            if os.path.basename(actual_dir):
                hint += f", в папке типа '{os.path.basename(actual_dir)}'"
            self.file_hints.append(hint)

            # Вторая подсказка - ложный диск
            drives = ['C:\\', 'D:\\', 'E:\\', 'F:\\']
            false_drives = [d for d in drives if d != root_dir and os.path.exists(d)]
            if false_drives:
                false_drive = random.choice(false_drives)
                self.file_hints.append(f"Или может быть на диске {false_drive[0]}")
            else:
                # Если только один диск, создаем ложную папку
                false_folders = ['Documents', 'Downloads', 'Desktop', 'Pictures', 'Music', 'Videos']
                self.file_hints.append(f"Или в папке '{random.choice(false_folders)}'")

        else:  # Unix/Mac
            self.file_hints.append(f"В корневой системе {root_dir}")

            false_roots = ['/home', '/tmp', '/var', '/usr']
            if actual_dir not in false_roots:
                self.file_hints.append(f"Или может быть в {random.choice(false_roots)}")
            else:
                self.file_hints.append("Или в пользовательских директориях")

    def check_file_guess(self, user_input):
        self.clear_text()
        self.clear_buttons()

        # Убираем лишние пробелы и приводим к нижнему регистру
        user_guess = user_input.strip().lower()
        correct_name = os.path.basename(self.secret_file_fullpath).lower()

        self.print_text("=" * 50)
        self.print_text(f"Ваш ответ: {user_input}")
        self.print_text(f"Правильный ответ: {os.path.basename(self.secret_file_fullpath)}")
        self.print_text(f"Файл был создан по пути: {self.secret_file_fullpath}")

        # Проверяем ответ
        if user_guess == correct_name:
            self.money += self.value
            if ICantStopWin:
                pygame.mixer.Channel(0).play(pygame.mixer.Sound(ICantStopWin))
            self.print_text(f"\n🎉 Поздравляем! Вы нашли файл!")
            self.print_text(f"💰 Вы выиграли {self.value} золотых!")
        else:
            self.money -= self.value
            if OhDangIt:
                pygame.mixer.Channel(0).play(pygame.mixer.Sound(OhDangIt))
            self.print_text(f"\n😞 К сожалению, вы не угадали.")
            self.print_text(f"💸 Вы проиграли {self.value} золотых.")

        # Пытаемся удалить созданный файл
        try:
            if os.path.exists(self.secret_file_fullpath):
                os.remove(self.secret_file_fullpath)
                self.print_text("\n🗑️ Созданный файл был удален.")
        except:
            pass

        self.print_text(f"\nТекущий баланс: {self.money}💰")
        self.print_text("=" * 50)

        tk.Button(self.button_frame, text="🎰 Сыграть ещё раз",
                  command=self.start_casino).pack(side=tk.LEFT, padx=5)
        tk.Button(self.button_frame, text="📋 В главное меню",
                  command=self.show_main_menu).pack(side=tk.LEFT, padx=5)

    def start_shop(self):
        if Select:
            pygame.mixer.Channel(0).play(pygame.mixer.Sound(Select), maxtime=600)
        if Shop:
            pygame.mixer.music.load(Shop)
            pygame.mixer.music.play(-1)

        self.talkfirst = ""
        self.clear_text()
        self.clear_buttons()

        self.print_text(f"Ну привет {self.gamername}")
        self.print_text("У меня есть несколько товаров для тебя. Но учти все стоит денег хехехе")
        self.print_text(f"\nТекущий товар 1: {self.meleeitemsshop}")
        self.print_text(f"Текущий товар 2: {self.armoritemsshop}")
        self.print_text(f"Спецтовар: {self.specitemshop}")
        self.print_text(f"Семена: {self.seedsshop}")
        self.print_text(f"\nВаши деньги: {self.money}💰")

        self.print_text("\nВыберите действие:")

        tk.Button(self.button_frame, text="Просмотреть первый товар", command=self.view_item1).pack(pady=2)
        tk.Button(self.button_frame, text="Просмотреть второй товар", command=self.view_item2).pack(pady=2)
        tk.Button(self.button_frame, text="Просмотреть спецтовар", command=self.view_spec_item).pack(pady=2)
        tk.Button(self.button_frame, text="Просмотреть семена", command=self.view_seeds).pack(pady=2)
        tk.Button(self.button_frame, text="Обновить товары (15💰)", command=self.refresh_shop).pack(pady=2)
        tk.Button(self.button_frame, text="Выйти", command=self.show_main_menu).pack(pady=2)

    def view_item1(self):
        self.clear_text()
        self.clear_buttons()

        item = self.meleeitemsshop
        price = self.item_prices.get(item, 0)
        desc = self.item_descriptions.get(item, "Описание отсутствует")

        self.print_text(f"Товар: {desc}")
        self.print_text(f"Цена: {price}💰")
        self.print_text(f"Ваши деньги: {self.money}💰")

        tk.Button(self.button_frame, text="Купить", command=lambda: self.buy_item(item, price)).pack(side=tk.LEFT,
                                                                                                     padx=5)
        tk.Button(self.button_frame, text="Назад", command=self.start_shop).pack(side=tk.LEFT, padx=5)

    def view_item2(self):
        self.clear_text()
        self.clear_buttons()

        item = self.armoritemsshop
        price = self.item_prices.get(item, 0)
        desc = self.item_descriptions.get(item, "Описание отсутствует")

        self.print_text(f"Товар: {desc}")
        self.print_text(f"Цена: {price}💰")
        self.print_text(f"Ваши деньги: {self.money}💰")

        tk.Button(self.button_frame, text="Купить", command=lambda: self.buy_item(item, price)).pack(side=tk.LEFT,
                                                                                                     padx=5)
        tk.Button(self.button_frame, text="Назад", command=self.start_shop).pack(side=tk.LEFT, padx=5)

    def view_spec_item(self):
        self.clear_text()
        self.clear_buttons()

        item = self.specitemshop
        price = self.item_prices.get(item, 0)
        desc = self.item_descriptions.get(item, "Описание отсутствует")

        self.print_text(f"Товар: {desc}")
        self.print_text(f"Цена: {price}💰")
        self.print_text(f"Ваши деньги: {self.money}💰")

        tk.Button(self.button_frame, text="Купить", command=lambda: self.buy_item(item, price)).pack(side=tk.LEFT,
                                                                                                     padx=5)
        tk.Button(self.button_frame, text="Назад", command=self.start_shop).pack(side=tk.LEFT, padx=5)

    def view_seeds(self):
        self.clear_text()
        self.clear_buttons()

        item = self.seedsshop
        price = self.item_prices.get(item, 0)
        desc = self.item_descriptions.get(item, "Описание отсутствует")

        self.print_text(f"Товар: {desc}")
        self.print_text(f"Цена: {price}💰")
        self.print_text(f"Ваши деньги: {self.money}💰")

        tk.Button(self.button_frame, text="Купить", command=lambda: self.buy_item(item, price)).pack(side=tk.LEFT,
                                                                                                     padx=5)
        tk.Button(self.button_frame, text="Назад", command=self.start_shop).pack(side=tk.LEFT, padx=5)

    def buy_item(self, item, price):
        if self.money >= price:
            self.money -= price

            # Добавляем предмет
            if item in ["fighting_gloves", "fighting_sword", "The_epic_sword"]:
                if item == "fighting_gloves":
                    self.item_gloves += 1
                elif item == "fighting_sword":
                    self.item_sword += 1
                else:
                    self.item_epicsword += 1

            elif item in ["armorbasic", "armorheavy", "thewarriorarmor"]:
                if item == "armorbasic":
                    self.item_basicarmor += 1
                elif item == "armorheavy":
                    self.item_armorheavy += 1
                else:
                    self.item_warriorarmor += 1

            elif item in ["The_happy_gnome", "+PARRY", "Trickstab_knife", "Old_Legendary_Amulet"]:
                if item == "The_happy_gnome":
                    self.item_gnome += 1
                elif item == "+PARRY":
                    self.item_parry += 1
                elif item == "Trickstab_knife":
                    self.item_trickstab += 1
                else:
                    self.item_oldamulet += 1

            elif item in ["HealPotion", "HealthPotion", "PowerPotion"]:
                if item == "HealPotion":
                    self.playerhp = self.playertotalhp
                    self.print_text("Вы выпили зелье лечения! Здоровье восстановлено!")
                elif item == "HealthPotion":
                    self.playerhp = self.playertotalhp
                    self.print_text("Вы выпили зелье здоровья! Здоровье восстановлено!")
                elif item == "PowerPotion":
                    self.playerpunchpower *= 2
                    self.playerpower = self.playerpunchpower
                    if self.glovesequiptoken:
                        self.playerpower = self.playerpunchpower * 2
                    elif self.swordequiptoken:
                        self.playerpower = self.playerpunchpower * 3
                    elif self.epicswordequiptoken:
                        self.playerpower = self.playerpunchpower * 4
                    self.print_text("Вы выпили зелье силы! Атака увеличена в 2 раза!")

            elif item in ["Melon", "Potato", "GoldenCarrot"]:
                if item == "Melon":
                    self.item_melonseeds += 1
                elif item == "Potato":
                    self.item_potatoseeds += 1
                else:
                    self.item_gcarrotseeds += 1

            if Select:
                pygame.mixer.Channel(0).play(pygame.mixer.Sound(Select), maxtime=600)
            self.print_text(random.choice(self.shop_man_answer_got_money))
            self.print_text(f"Предмет куплен! Осталось денег: {self.money}💰")
        else:
            if IDK:
                pygame.mixer.Channel(0).play(pygame.mixer.Sound(IDK), maxtime=600)
            self.print_text(random.choice(self.shop_man_answers_no_money))

    def refresh_shop(self):
        if self.money >= 15:
            self.money -= 15
            self.meleeitemsshop = random.choice(self.meleeitemcatalog)
            self.armoritemsshop = random.choice(self.armoritemscatalog)
            self.specitemshop = random.choice(self.spec_itemcatalog)
            self.seedsshop = random.choice(self.seedsshopcatalog)
            if Select:
                pygame.mixer.Channel(0).play(pygame.mixer.Sound(Select), maxtime=600)
            self.print_text("Товары обновлены!")
            self.start_shop()
        else:
            self.print_text("Недостаточно денег для обновления!")

    def show_inventory(self):
        if Select:
            pygame.mixer.Channel(0).play(pygame.mixer.Sound(Select), maxtime=600)

        self.clear_text()
        self.clear_buttons()

        self.print_text("=== ВАШ ИНВЕНТАРЬ ===")
        self.print_text(f"Боевые перчатки: {self.item_gloves}")
        self.print_text(f"Мечи: {self.item_sword}")
        self.print_text(f"Эпические мечи: {self.item_epicsword}")
        self.print_text(f"Базовая броня: {self.item_basicarmor}")
        self.print_text(f"Тяжелая броня: {self.item_armorheavy}")
        self.print_text(f"Броня воина: {self.item_warriorarmor}")
        self.print_text(f"Гномы: {self.item_gnome}")
        self.print_text(f"Паррирование: {self.item_parry}")
        self.print_text(f"Удар в спину: {self.item_trickstab}")
        self.print_text(f"Амулеты: {self.item_oldamulet}")
        self.print_text(f"Семена арбуза: {self.item_melonseeds}")
        self.print_text(f"Семена картошки: {self.item_potatoseeds}")
        self.print_text(f"Семена золотой моркови: {self.item_gcarrotseeds}")

        self.print_text("\n=== ЭКИПИРОВКА ===")
        weapon_text = "Оружие: "
        if self.glovesequiptoken:
            weapon_text += "Перчатки"
        elif self.swordequiptoken:
            weapon_text += "Меч"
        elif self.epicswordequiptoken:
            weapon_text += "Эпический меч"
        else:
            weapon_text += "Нет"
        self.print_text(weapon_text)

        armor_text = "Броня: "
        if self.basicarmortoken:
            armor_text += "Базовая"
        elif self.heavyarmortoken:
            armor_text += "Тяжелая"
        elif self.elitearmortoken:
            armor_text += "Воина"
        else:
            armor_text += "Нет"
        self.print_text(armor_text)

        spec_text = "Спецпредмет: "
        if self.gnomeequiptoken:
            spec_text += "Гном"
        elif self.parryequiptoken:
            spec_text += "Паррирование"
        elif self.trickstabequiptoken:
            spec_text += "Удар в спину"
        elif self.amuletequiptoken:
            spec_text += "Амулет"
        else:
            spec_text += "Нет"
        self.print_text(spec_text)

        self.print_text("\nВыберите действие:")

        tk.Button(self.button_frame, text="Экипировать оружие", command=self.equip_weapons).pack(pady=2)
        tk.Button(self.button_frame, text="Экипировать броню", command=self.equip_armor).pack(pady=2)
        tk.Button(self.button_frame, text="Экипировать спецпредмет", command=self.equip_special).pack(pady=2)
        tk.Button(self.button_frame, text="Снять всё", command=self.unequip_all).pack(pady=2)
        tk.Button(self.button_frame, text="Вернуться в меню", command=self.show_main_menu).pack(pady=2)

    def equip_weapons(self):
        self.clear_buttons()
        self.print_text("\nВыберите оружие для экипировки:")

        if self.item_gloves > 0:
            tk.Button(self.button_frame, text="Перчатки (х2 атака)", command=self.equip_gloves).pack(pady=2)
        if self.item_sword > 0:
            tk.Button(self.button_frame, text="Меч (х3 атака)", command=self.equip_sword).pack(pady=2)
        if self.item_epicsword > 0:
            tk.Button(self.button_frame, text="Эпический меч (х4 атака)", command=self.equip_epicsword).pack(pady=2)

        tk.Button(self.button_frame, text="Назад", command=self.show_inventory).pack(pady=2)

    def equip_gloves(self):
        if not (self.glovesequiptoken or self.swordequiptoken or self.epicswordequiptoken):
            self.playerpower = self.playerpunchpower * 2
            self.glovesequiptoken = 1
            if TAKEAWEAPON:
                pygame.mixer.Channel(0).play(pygame.mixer.Sound(TAKEAWEAPON), maxtime=600)
            self.print_text("Перчатки экипированы!")
        else:
            self.print_text("Сначала снимите текущее оружие!")

    def equip_sword(self):
        if not (self.glovesequiptoken or self.swordequiptoken or self.epicswordequiptoken):
            self.playerpower = self.playerpunchpower * 3
            self.swordequiptoken = 1
            if TAKEAWEAPON:
                pygame.mixer.Channel(0).play(pygame.mixer.Sound(TAKEAWEAPON), maxtime=600)
            self.print_text("Меч экипирован!")
        else:
            self.print_text("Сначала снимите текущее оружие!")

    def equip_epicsword(self):
        if not (self.glovesequiptoken or self.swordequiptoken or self.epicswordequiptoken):
            self.playerpower = self.playerpunchpower * 4
            self.epicswordequiptoken = 1
            if TAKEAWEAPON:
                pygame.mixer.Channel(0).play(pygame.mixer.Sound(TAKEAWEAPON), maxtime=600)
            self.print_text("Эпический меч экипирован!")
        else:
            self.print_text("Сначала снимите текущее оружие!")

    def equip_armor(self):
        self.clear_buttons()
        self.print_text("\nВыберите броню для экипировки:")

        if self.item_basicarmor > 0:
            tk.Button(self.button_frame, text="Базовая броня (х2 защита)", command=self.equip_basic_armor).pack(pady=2)
        if self.item_armorheavy > 0:
            tk.Button(self.button_frame, text="Тяжелая броня (х3 защита)", command=self.equip_heavy_armor).pack(pady=2)
        if self.item_warriorarmor > 0:
            tk.Button(self.button_frame, text="Броня воина (х4 защита)", command=self.equip_warrior_armor).pack(pady=2)

        tk.Button(self.button_frame, text="Назад", command=self.show_inventory).pack(pady=2)

    def equip_basic_armor(self):
        if not (self.basicarmortoken or self.heavyarmortoken or self.elitearmortoken):
            self.playertotalhp = self.playermaxhp * 2
            self.basicarmortoken = 1
            if TAKEAWEAPON:
                pygame.mixer.Channel(0).play(pygame.mixer.Sound(TAKEAWEAPON), maxtime=600)
            self.print_text("Базовая броня экипирована!")
        else:
            self.print_text("Сначала снимите текущую броню!")

    def equip_heavy_armor(self):
        if not (self.basicarmortoken or self.heavyarmortoken or self.elitearmortoken):
            self.playertotalhp = self.playermaxhp * 3
            self.playerdefence = self.playerdefencestarter * 2
            self.heavyarmortoken = 1
            if TAKEAWEAPON:
                pygame.mixer.Channel(0).play(pygame.mixer.Sound(TAKEAWEAPON), maxtime=600)
            self.print_text("Тяжелая броня экипирована!")
        else:
            self.print_text("Сначала снимите текущую броню!")

    def equip_warrior_armor(self):
        if not (self.basicarmortoken or self.heavyarmortoken or self.elitearmortoken):
            self.playertotalhp = self.playermaxhp * 4
            self.playerdefence = self.playerdefencestarter * 3
            self.elitearmortoken = 1
            if TAKEAWEAPON:
                pygame.mixer.Channel(0).play(pygame.mixer.Sound(TAKEAWEAPON), maxtime=600)
            self.print_text("Броня воина экипирована!")
        else:
            self.print_text("Сначала снимите текущую броню!")

    def equip_special(self):
        self.clear_buttons()
        self.print_text("\nВыберите спецпредмет:")

        if self.item_gnome > 0:
            tk.Button(self.button_frame, text="Гном", command=self.equip_gnome).pack(pady=2)
        if self.item_parry > 0:
            tk.Button(self.button_frame, text="Паррирование", command=self.equip_parry).pack(pady=2)
        if self.item_trickstab > 0:
            tk.Button(self.button_frame, text="Удар в спину", command=self.equip_trickstab).pack(pady=2)
        if self.item_oldamulet > 0:
            tk.Button(self.button_frame, text="Амулет", command=self.equip_amulet).pack(pady=2)

        tk.Button(self.button_frame, text="Назад", command=self.show_inventory).pack(pady=2)

    def equip_gnome(self):
        if not (self.gnomeequiptoken or self.parryequiptoken or self.trickstabequiptoken or self.amuletequiptoken):
            self.gnomeequiptoken = 1
            # Эффект гнома: снижение статов, но бонус к деньгам
            self.playerdefence -= 4
            self.playerpower -= 4
            if TAKEAWEAPON:
                pygame.mixer.Channel(0).play(pygame.mixer.Sound(TAKEAWEAPON), maxtime=600)
            self.print_text("Гном экипирован (зря.....)")
        else:
            self.print_text("Сначала снимите текущий спецпредмет!")

    def equip_parry(self):
        if not (self.gnomeequiptoken or self.parryequiptoken or self.trickstabequiptoken or self.amuletequiptoken):
            self.parryequiptoken = 1
            if TAKEAWEAPON:
                pygame.mixer.Channel(0).play(pygame.mixer.Sound(TAKEAWEAPON), maxtime=600)
            self.print_text("Паррирование экипировано")
        else:
            self.print_text("Сначала снимите текущий спецпредмет!")

    def equip_trickstab(self):
        if not (self.gnomeequiptoken or self.parryequiptoken or self.trickstabequiptoken or self.amuletequiptoken):
            self.trickstabequiptoken = 1
            if TAKEAWEAPON:
                pygame.mixer.Channel(0).play(pygame.mixer.Sound(TAKEAWEAPON), maxtime=600)
            self.print_text("Удар в спину экипирован")
        else:
            self.print_text("Сначала снимите текущий спецпредмет!")

    def equip_amulet(self):
        if not (self.gnomeequiptoken or self.parryequiptoken or self.trickstabequiptoken or self.amuletequiptoken):
            self.amuletequiptoken = 1
            if TAKEAWEAPON:
                pygame.mixer.Channel(0).play(pygame.mixer.Sound(TAKEAWEAPON), maxtime=600)
            self.print_text("Амулет экипирован")
        else:
            self.print_text("Сначала снимите текущий спецпредмет!")

    def unequip_all(self):
        # Снимаем оружие
        self.playerpower = self.playerpunchpower
        self.glovesequiptoken = 0
        self.swordequiptoken = 0
        self.epicswordequiptoken = 0

        # Снимаем броню
        self.playerdefence = self.playerdefencestarter
        self.playertotalhp = self.playermaxhp
        self.basicarmortoken = 0
        self.heavyarmortoken = 0
        self.elitearmortoken = 0

        # Снимаем спецпредметы
        self.amuletequiptoken = 0
        self.trickstabequiptoken = 0
        self.parryequiptoken = 0
        self.gnomeequiptoken = 0
        # Отменяем эффект гнома
        self.playerdefence += 4
        self.playerpower += 4

        self.print_text("Вся экипировка снята!")
        self.show_inventory()

    def run(self):
        self.root.mainloop()


def main():
    game = GameGUI()


if __name__ == "__main__":
    main()