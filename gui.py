from tkinter import *
from tkinter import ttk, messagebox, filedialog
from parsing_logic import parser_vacancies
from settings import settings, regions_dict
from utils import save_to_excel
from datetime import datetime
import re
import os
import threading
import sv_ttk

def start_gui():
    root = Tk()
    root.title("Поиск вакансий")
    root.geometry("400x400")

    sv_ttk.set_theme("dark")

    def update_region_options(event):
        selected_region = combobox_rg_name.get()

        combobox_rg_name.selection_clear()
        combobox_rg_name.icursor("end")

        if selected_region == "Любая":
            combobox_dist_name.set("")
            combobox_dist_name["values"] = []
        else:
            combobox_dist_name.set("Любой")
            combobox_dist_name["values"] = ["Любой"] + regions_dict.get(selected_region, [])
    

    def on_district_selected(event):
        combobox_dist_name.selection_clear()  # Снимаем выделение
        combobox_dist_name.icursor("end")


    # GUI elements
    label_vacancy = ttk.Label(root, text="Введите вакансию:")
    label_vacancy.pack()
    entry_vacancy = ttk.Entry(root, width=30)
    entry_vacancy.pack(pady=5)

    label_region = ttk.Label(root, text="Выберите область:")
    label_region.pack()
    combobox_rg_name = ttk.Combobox(root, values=["Любая"] + list(regions_dict.keys()), state="readonly")
    combobox_rg_name.bind('<<ComboboxSelected>>', update_region_options)
    combobox_rg_name.pack(pady=5)

    label_district = ttk.Label(text="Выберите район:", font=("Arial", 11))
    label_district.pack()

    combobox_dist_name = ttk.Combobox(root, state="readonly")
    combobox_dist_name.bind('<<ComboboxSelected>>', on_district_selected)
    combobox_dist_name.pack(pady=5)

    """Open the settings window."""
    def open_settings():
        """Open the settings window."""
        def toggle_headless():
            settings["headless"] = headless_var.get()

        def set_window_size():
            selected_size = window_size_combobox.get()
            if selected_size:
                width, height = map(int, selected_size.split("x"))
                settings["window_width"] = width
                settings["window_height"] = height

        def choose_default_folder():
            folder_path = filedialog.askdirectory(title="Выберите папку для сохранения")
            if folder_path:
                settings["default_save_folder"] = folder_path

        settings_window = Toplevel(root)
        settings_window.title("Настройки")
        settings_window.geometry("300x300")

        # Headless mode checkbox
        headless_var = BooleanVar(value=settings["headless"])
        headless_checkbox = ttk.Checkbutton(
            settings_window, text="Режим без интерфейса (Headless)", variable=headless_var, command=toggle_headless
        )
        headless_checkbox.pack(pady=10)

        # Browser window size options
        window_sizes = ["1024x768", "1280x720", "1366x768", "1440x900", "1600x900" "1920x1080"]
        window_size_label = ttk.Label(settings_window, text="Размер окна браузера:")
        window_size_label.pack(pady=5)
        window_size_combobox = ttk.Combobox(settings_window, values=window_sizes, state="readonly")
        current_size = f'{settings.get("window_width", 1024)}x{settings.get("window_height", 768)}'
        window_size_combobox.set(current_size)
        window_size_combobox.pack(pady=5)

        # Default save folder button
        folder_button = ttk.Button(settings_window, text="Выбрать папку для сохранения", command=choose_default_folder)
        folder_button.pack(pady=10)

        # Save button
        save_button = ttk.Button(settings_window, text="Сохранить", command=set_window_size)
        save_button.pack(pady=10)


    def start_parsing():
        vacancy = entry_vacancy.get().strip() or "all"
        region = combobox_rg_name.get().strip()
        district = combobox_dist_name.get().strip() or "any"

            # Generate a default file name
        current_date = datetime.now().strftime("%d-%m-%Y")  # Format: DD-MM-YYYY
        default_filename = f"{vacancy}_{district}_{current_date}".replace(" ", "_")  # Replace spaces with underscores

        # Remove invalid characters for file names
        default_filename = re.sub(r"[^\w\-_\.]", "", default_filename)

        # Ensure the filename is not empty after sanitization
        if not default_filename:
            default_filename = "default_filename"

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")],
            initialfile=default_filename,
            title="Сохранить файл как"
        )
        if not file_path:
            return  # Отмена сохранения

        def run_parsing():
        # Run the parser and save the data
            data = parser_vacancies(vacancy, region, district, progress_bar, label_status, root)
            if data:
                save_to_excel(data, file_path)  # Save the parsed data to Excel
                if messagebox.askyesno("Открыть файл", "Данные успешно сохранены. Хотите открыть сохраненный файл?"):
                    try:
                        os.startfile(file_path)  # Open the file using the default application
                    except Exception as e:
                        messagebox.showerror("Ошибка", f"Не удалось открыть файл: {str(e)}")

            # Run parsing in a separate thread
        parsing_thread = threading.Thread(target=run_parsing)
        parsing_thread.start()

    progress_bar = ttk.Progressbar(root, length=200, mode="determinate")
    progress_bar.pack(pady=10)

    label_status = ttk.Label(root, text="Готов к работе")
    label_status.pack()

    btn = ttk.Button(root, text="Начать поиск", command=start_parsing)
    btn.pack(pady=20)

    btn_settings = ttk.Button(root, text="Настройки", command=open_settings)
    btn_settings.pack(pady=5)

    root.mainloop()