import time
import random
import logging
import traceback
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from driver_utils import init_driver
from utils import save_to_excel
from settings import settings, regions_dict

class SmartWaiter:
    """Класс для умных ожиданий"""
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def for_ajax_complete(self):
        def is_ajax_done(driver):
            try:
                return driver.execute_script("return window.jQuery && jQuery.active === 0")
            except:
                return True
        return self.wait.until(is_ajax_done)

    def for_element_visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def for_element_clickable(self, locator):
        return self.wait.until(EC.element_to_be_clickable(locator))

    def for_select_options_loaded(self, select_element):
        def options_loaded(driver):
            return len(select_element.options) > 1
        return self.wait.until(options_loaded)


class VacancyParser:

    def __init__(self, vacancy, region, district, label_status, progress_bar, root):
        self.vacancy = vacancy
        self.region = region
        self.district = district
        self.label_status = label_status
        self.progress_bar = progress_bar
        self.root = root
        self.data = []
        self.driver = init_driver()
        self.waiter = SmartWaiter(self.driver)

    def log_and_update(self, message, progress=None):
        """Обновление статуса и логирование"""
        logging.info(message)
        self.label_status.config(text=message)
        self.root.update_idletasks()
        if progress is not None:
            self.progress_bar["value"] = progress

    def open_search_page(self):
        """Открыть страницу поиска"""
        self.driver.get("https://gsz.gov.by/registration/vacancy-search/?profession=")
        self.waiter.for_ajax_complete()

    def fill_search_form(self):
        """Заполнить форму поиска"""
        search_field = self.waiter.for_element_clickable((By.ID, "id_profession"))
        search_field.clear()
        search_field.send_keys(self.vacancy)

        if self.region and self.region != "Любая":
            region_select = self.waiter.for_element_clickable((By.ID, "id_region"))
            Select(region_select).select_by_visible_text(self.region)
            self.waiter.for_ajax_complete()

            if self.district and self.district != "Любой":
                district_select = self.waiter.for_element_clickable((By.ID, "id_district"))
                self.waiter.for_select_options_loaded(Select(district_select))
                Select(district_select).select_by_visible_text(self.district)
                self.waiter.for_ajax_complete()

        search_btn = self.waiter.for_element_clickable((By.CLASS_NAME, "theme-btn"))
        search_btn.click()
        self.waiter.for_ajax_complete()

    def get_max_page(self):
        """Определить количество страниц"""
        soup = BeautifulSoup(self.driver.page_source, "lxml")
        pagination = soup.find("ul", class_="pagination")
        max_page = 1
        if pagination:
            for link in pagination.find_all("a", class_="page-link"):
                try:
                    page_num = int(link.text.strip())
                    max_page = max(max_page, page_num)
                except ValueError:
                    continue
        return max_page

    def parse_single_page(self, soup, start_index):
        """Парсинг одной страницы"""
        job_blocks = soup.find_all("div", class_="col-12 col-md-9 col-lg-9 order-2 mt-4 mt-md-0")
        page_data = []

        for n, job in enumerate(job_blocks, start=start_index + 1):
            try:
                job_title_elem = job.find("a", class_="debounced-link")
                salary_elem = job.find("span", class_="salary")
                employer_elem = job.find(class_="org w-100").find("a") if job.find(class_="org w-100") else None
                education_elem = job.find("span", class_="fa-graduation-cap")
                address_elem = job.find("span", class_="address")
                additional_info_elem = job.find("span", title="Дополнительная информация")

                page_data.append({
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
                logging.warning(f"Ошибка при парсинге вакансии №{n}: {str(e)}\n{traceback.format_exc()}")
                continue

        return page_data

    def parse_pages(self):
        """Парсинг всех страниц"""
        try:
            self.open_search_page()
            self.log_and_update("Заполнение формы поиска...")
            self.fill_search_form()

            self.log_and_update("Определение количества страниц...")
            max_page = self.get_max_page()
            self.progress_bar["maximum"] = max_page

            self.log_and_update(f"Найдено страниц: {max_page}")

            for page in range(1, max_page + 1):
                for attempt in range(3):
                    try:
                        if page > 1:
                            new_url = f"{self.driver.current_url.split('&page=')[0]}&page={page}"
                            self.driver.get(new_url)
                            self.waiter.for_ajax_complete()

                        time.sleep(random.uniform(1.5, 3.0))  # рандомная задержка

                        soup = BeautifulSoup(self.driver.page_source, "lxml")
                        page_data = self.parse_single_page(soup, len(self.data))
                        self.data.extend(page_data)

                        self.log_and_update(f"Обработано {page}/{max_page} страниц", progress=page)
                        break

                    except Exception as e:
                        logging.warning(f"Ошибка при обработке страницы {page} (попытка {attempt + 1}): {str(e)}")
                        time.sleep(random.uniform(5, 10))
                        if attempt == 2:
                            logging.error(f"Не удалось обработать страницу {page} после 3 попыток.")

            return self.data

        finally:
            try:
                self.driver.quit()
            except:
                pass

