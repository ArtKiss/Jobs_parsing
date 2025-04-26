from tkinter import *
from tkinter import ttk, messagebox, filedialog
from parsing_logic import VacancyParser
from settings import settings, regions_dict, save_settings
from utils import save_to_excel
from datetime import datetime
import re
import os
import threading
import sv_ttk

def start_gui():
    root = Tk()
    root.title("Поиск вакансий")
    root.geometry("500x500")
    sv_ttk.set_theme(settings.get("theme", "dark"))

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    # ========== Вкладка: Поиск вакансий ==========
    search_tab = Frame(notebook)
    notebook.add(search_tab, text="Поиск вакансий")

    label_vacancy = ttk.Label(search_tab, text="Введите вакансию:")
    label_vacancy.pack()
    entry_vacancy = ttk.Entry(search_tab, width=30)
    entry_vacancy.pack(pady=5)

    label_region = ttk.Label(search_tab, text="Выберите область:")
    label_region.pack()
    combobox_rg_name = ttk.Combobox(search_tab, values=["Любая"] + list(regions_dict.keys()), state="readonly")
    combobox_rg_name.pack(pady=5)

    label_district = ttk.Label(search_tab, text="Выберите район:")
    label_district.pack()
    combobox_dist_name = ttk.Combobox(search_tab, state="readonly")
    combobox_dist_name.pack(pady=5)

    label_status = ttk.Label(search_tab, text="Готов к работе")
    label_status.pack()

    progress_bar = ttk.Progressbar(search_tab, length=200, mode="determinate")
    progress_bar.pack(pady=10)

    def update_region_options(event):
        selected_region = combobox_rg_name.get()
        if selected_region == "Любая":
            combobox_dist_name.set("")
            combobox_dist_name["values"] = []
        else:
            combobox_dist_name.set("Любой")
            combobox_dist_name["values"] = ["Любой"] + regions_dict.get(selected_region, [])

    def on_district_selected(event):
        combobox_dist_name.selection_clear()
        combobox_dist_name.icursor("end")

    combobox_rg_name.bind('<<ComboboxSelected>>', update_region_options)
    combobox_dist_name.bind('<<ComboboxSelected>>', on_district_selected)

    def start_parsing():
        vacancy = entry_vacancy.get().strip()            
        region = combobox_rg_name.get().strip()
        district = combobox_dist_name.get().strip()

        vacancy_for_file_name = entry_vacancy.get().strip() or 'all'
        region_for_file_name = combobox_rg_name.get().strip() or 'any'
        district_for_file_name = combobox_dist_name.get().strip() or 'any'

        current_date = datetime.now().strftime("%d-%m-%Y")
        default_filename = f"{vacancy_for_file_name}_{region_for_file_name}_{district_for_file_name}_{current_date}".replace(" ", "_")
        default_filename = re.sub(r"[^\w\-_\.]", "", default_filename)

        if not default_filename:
            default_filename = "default_filename"

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")],
            initialfile=default_filename,
            title="Сохранить файл как"
        )
        if not file_path:
            return

        def run_parsing():
            parser = VacancyParser(vacancy, region, district, label_status, progress_bar, root)
            data = parser.parse_pages()
            if data:
                save_to_excel(data, file_path)
                if messagebox.askyesno("Открыть файл", "Данные успешно сохранены. Хотите открыть файл?"):
                    try:
                        os.startfile(file_path)
                    except Exception as e:
                        messagebox.showerror("Ошибка", f"Не удалось открыть файл: {str(e)}")

        threading.Thread(target=run_parsing).start()

    btn = ttk.Button(search_tab, text="Начать поиск", command=start_parsing)
    btn.pack(pady=20)

    # ========== Вкладка: Настройки ==========
    settings_tab = Frame(notebook)
    notebook.add(settings_tab, text="Настройки")

    # Режим без интерфейса
    headless_var = BooleanVar(value=settings["headless"])
    headless_checkbox = ttk.Checkbutton(
        settings_tab, text="Режим без интерфейса (Headless)", variable=headless_var
    )
    headless_checkbox.pack(pady=10)

    # Размер окна браузера
    window_sizes = ["1024x768", "1280x720", "1366x768", "1440x900", "1600x900", "1920x1080"]
    window_size_label = ttk.Label(settings_tab, text="Размер окна браузера:")
    window_size_label.pack(pady=5)
    window_size_combobox = ttk.Combobox(settings_tab, values=window_sizes, state="readonly")
    current_size = f'{settings.get("window_width", 1024)}x{settings.get("window_height", 768)}'
    window_size_combobox.set(current_size)
    window_size_combobox.pack(pady=5)

    # Тема интерфейса
    theme_label = ttk.Label(settings_tab, text="Тема интерфейса:")
    theme_label.pack(pady=5)
    theme_var = StringVar(value=settings.get("theme", "dark"))
    theme_combobox = ttk.Combobox(settings_tab, values=["light", "dark"], textvariable=theme_var, state="readonly")
    theme_combobox.pack(pady=5)

    # Папка по умолчанию
    def choose_default_folder():
        folder_path = filedialog.askdirectory(title="Выберите папку для сохранения")
        if folder_path:
            settings["default_save_folder"] = folder_path
            default_folder_label.config(text=f"📁 {folder_path}")

    folder_button = ttk.Button(settings_tab, text="Выбрать папку для сохранения", command=choose_default_folder)
    folder_button.pack(pady=10)

    default_folder_label = ttk.Label(settings_tab, text=f"📁 {settings.get('default_save_folder', '')}")
    default_folder_label.pack()

    # Метка подтверждения
    confirm_label = ttk.Label(settings_tab, text="", foreground="green")
    confirm_label.pack(pady=5)

    def save_all_settings():
        # Headless
        settings["headless"] = headless_var.get()

        # Window size
        selected_size = window_size_combobox.get()
        if selected_size:
            width, height = map(int, selected_size.split("x"))
            settings["window_width"] = width
            settings["window_height"] = height

        # Theme
        selected_theme = theme_var.get()
        settings["theme"] = selected_theme
        sv_ttk.set_theme(selected_theme)

        save_settings(settings)

        # Показать подтверждение
        confirm_label.config(text="✅ Настройки сохранены")
        settings_tab.after(2000, lambda: confirm_label.config(text=""))

    save_all_button = ttk.Button(settings_tab, text="Сохранить настройки", command=save_all_settings)
    save_all_button.pack(pady=15)

    root.mainloop()