from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from driver_utils import init_driver
from utils import save_to_excel
from settings import settings, regions_dict
import logging
import time


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("parser.log"),
        logging.StreamHandler()
    ]
)


class SmartWaiter:
    """Класс для умных ожиданий с кастомными условиями"""
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)

    def for_ajax_complete(self):
        """Ждём завершения jQuery AJAX, если jQuery определён"""
        def is_ajax_done(driver):
            try:
                return driver.execute_script("return window.jQuery && jQuery.active === 0")
            except:
                return True  # если jQuery нет, просто пропускаем ожидание
        return self.wait.until(is_ajax_done)

    def for_element_visible(self, locator):
        """Ждем появления и видимости элемента"""
        return self.wait.until(
            EC.visibility_of_element_located(locator)
        )

    def for_element_clickable(self, locator):
        """Ждем кликабельности элемента"""
        return self.wait.until(
            EC.element_to_be_clickable(locator)
        )

    def for_select_options_loaded(self, select_element):
        """Ждем загрузки опций в select"""
        def options_loaded(driver):
            return len(select_element.options) > 1
        return self.wait.until(options_loaded)


def get_max_page(soup):
    """Determine the maximum number of pages."""
    max_page = 1
    pagination = soup.find("ul", class_="pagination")
    if pagination:
        for link in pagination.find_all("a", class_="page-link"):
            try:
                page_num = int(link.text.strip())
                if page_num > max_page:
                    max_page = page_num
            except ValueError:
                continue
    return max_page


def parse_page_data(soup, start_index):
    """Extract job data from a page."""
    job_blocks = soup.find_all("div", class_="col-12 col-md-9 col-lg-9 order-2 mt-4 mt-md-0")
    data = []

    for n, job in enumerate(job_blocks, start=start_index + 1):
        try:
            job_title_elem = job.find("a", class_="debounced-link")
            salary_elem = job.find("span", class_="salary")
            employer_elem = job.find(class_="org w-100").find("a") if job.find(class_="org w-100") else None
            education_elem = job.find("span", class_="fa-graduation-cap")
            address_elem = job.find("span", class_="address")
            additional_info_elem = job.find("span", title="Дополнительная информация")

            data.append({
                "№": n,
                "Название вакансии": job_title_elem.text.strip() if job_title_elem else "Не указано",
                "Ссылка": f"https://gsz.gov.by{job.find('a').get('href')}" if job.find('a') else "Нет ссылки",
                "Зарплата": salary_elem.text if salary_elem else "Не указана",
                "Работодатель": employer_elem.text.strip() if employer_elem else "Не указан",
                "Образование": education_elem.find_next_sibling("span").text if education_elem else "Не указано",
                "Адрес": address_elem.text if address_elem else "Не указан",
                "Дополнительная информация": additional_info_elem.find_next_sibling("span").get_text(strip=True) 
                if additional_info_elem else "Нет информации"
            })
        except Exception as e:
            logging.warning(f"Ошибка при парсинге вакансии: {str(e)}")
            continue

    return data


def parser_vacancies(vacancy, region, district, progress_bar, label_status, root):
    """Main function to parse vacancies."""
    driver = init_driver()
    waiter = SmartWaiter(driver)
    data = []
    label_status.config(text="Инициализация драйвера...")
    root.update_idletasks()

    try:
        # Open search page
        driver.get("https://gsz.gov.by/registration/vacancy-search/?profession=")

        label_status.config(text="Ввод профессии...")
        root.update_idletasks()
        search_field = waiter.for_element_clickable((By.ID, "id_profession"))
        search_field.clear()
        search_field.send_keys(vacancy)

        # Выбор региона
        if region and region != "Любая":
            label_status.config(text="Выбор региона...")
            root.update_idletasks()
            region_select = waiter.for_element_clickable((By.ID, "id_region"))
            Select(region_select).select_by_visible_text(region)
            
            # Ждем обновления DOM после выбора региона
            waiter.for_ajax_complete()

            # Выбор района
            if district and district != "Любой":
                label_status.config(text="Выбор района...")
                root.update_idletasks()
                # Ждем пока список районов станет доступен для выбора
                district_select = waiter.for_element_clickable((By.ID, "id_district"))
                waiter.for_select_options_loaded(Select(district_select))
                Select(district_select).select_by_visible_text(district)
                waiter.for_ajax_complete()

        # Нажимаем кнопку поиска
        label_status.config(text="Запуск поиска...")
        root.update_idletasks()
        search_btn = waiter.for_element_clickable((By.CLASS_NAME, "theme-btn"))
        search_btn.click()
        waiter.for_ajax_complete()

        # Определяем количество страниц
        label_status.config(text="Определение количества страниц...")
        root.update_idletasks()
        soup = BeautifulSoup(driver.page_source, "lxml")
        max_page = get_max_page(soup)

        progress_bar["maximum"] = max_page
        label_status.config(text=f"Найдено страниц: {max_page}")
        root.update_idletasks()

        for page in range(1, max_page + 1):
            label_status.config(text=f"Обработка страницы {page}...")
            root.update_idletasks()

            # Переходим на страницу
            if page > 1:
                new_url = f"{driver.current_url.split('&page=')[0]}&page={page}"
                driver.get(new_url)
                waiter.for_ajax_complete()

            # Парсим данные
            soup = BeautifulSoup(driver.page_source, "lxml")
            page_data = parse_page_data(soup, len(data))
            data.extend(page_data)

            # Обновляем прогресс
            label_status.config(text=f"Обработано {page} из {max_page} страниц")
            root.update_idletasks()
            progress_bar["value"] = page
            
        return data

    except Exception as e:
        logging.error(f"Критическая ошибка в парсере: {str(e)}")
        return data
    finally:
        try:
            driver.quit()
        except:
            pass