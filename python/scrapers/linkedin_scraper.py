# python/scrapers/linkedin_scraper.py
from scrapers.base_scraper import BaseScraper
from utils.helpers import *
from config import *
from utils.open_chrome import *
from utils.search import *
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
    NoSuchWindowException,
    ElementNotInteractableException,
)
from dotenv import load_dotenv
import pyautogui

pyautogui.FAILSAFE = False

# Load configuration
load_dotenv()
username = os.environ.get("LINKEDIN_USERNAME")
password = os.environ.get("LINKEDIN_PASSWORD")


class LinkedInScraper(BaseScraper):
    """
    LinkedInScraper class to scrape jobs from LinkedIn
    """

    def __init__(self):
        super().__init__("https://www.linkedin.com/jobs")
        self.sort_by = "Most relevant"
        self.date_posted = "Past 24 hours"
        self.experience_level = ["Associate", "Entry level"]
        self.job_type = ["Full-time"]
        self.on_site = ["Remote"]
        self.location = ["Australia"]
        self.industry = []
        self.job_function = []
        self.job_titles = []

    def is_logged_in(self) -> bool:
        if driver.current_url == "https://www.linkedin.com/feed/":
            return True
        if try_linkText(driver, "Sign in"):
            return False
        if try_xp(driver, '//button[@type="submit" and contains(text(), "Sign in")]'):
            return False
        if try_linkText(driver, "Join now"):
            return False
        print_lg("Didn't find Sign in link, so assuming user is logged in!")
        return True

    def login(self) -> None:
        """
        Function to login for LinkedIn
        * Tries to login using given `username` and `password` from `secrets.py`
        * If failed, tries to login using saved LinkedIn profile button if available
        * If both failed, asks user to login manually
        """
        # Find the username and password fields and fill them with user credentials
        driver.get("https://www.linkedin.com/login")
        try:
            wait.until(
                EC.presence_of_element_located((By.LINK_TEXT, "Forgot password?"))
            )
            try:
                text_input_by_ID(driver, "username", username, 1)
            except Exception as e:
                print_lg("Couldn't find username field.")
                # print_lg(e)
            try:
                text_input_by_ID(driver, "password", password, 1)
            except Exception as e:
                print_lg("Couldn't find password field.")
                # print_lg(e)
            # Find the login submit button and click it
            driver.find_element(
                By.XPATH, '//button[@type="submit" and contains(text(), "Sign in")]'
            ).click()
        except Exception:
            try:
                profile_button = self.find_by_class(driver, "profile__details")
                profile_button.click()
            except Exception:
                print_lg("Couldn't Login!")

        try:
            # Wait until successful redirect, indicating successful login
            wait.until(
                EC.url_to_be("https://www.linkedin.com/feed/")
            )  # wait.until(EC.presence_of_element_located((By.XPATH, '//button[normalize-space(.)="Start a post"]')))
            return print_lg("Login successful!")
        except Exception as e:
            print_lg(
                "Seems like login attempt failed! Possibly due to wrong credentials or already logged in! Try logging in manually!"
            )
            # print_lg(e)

    # Find functions
    def find_by_class(
        self, driver: WebDriver, class_name: str, time: float = 5.0
    ) -> WebElement | Exception:
        return WebDriverWait(driver, time).until(
            EC.presence_of_element_located((By.CLASS_NAME, class_name))
        )

    def set_search_location(self) -> None:
        """
        Function to set search location
        """
        if search_location.strip():
            try:
                print_lg(f'Setting search location as: "{search_location.strip()}"')
                search_location_ele = try_xp(
                    driver,
                    ".//input[@aria-label='City, state, or zip code'and not(@disabled)]",
                    False,
                )  #  and not(@aria-hidden='true')]")
                text_input(
                    actions, search_location_ele, search_location, "Search Location"
                )
            except ElementNotInteractableException:
                try_xp(
                    driver,
                    ".//label[@class='jobs-search-box__input-icon jobs-search-box__keywords-label']",
                )
                actions.send_keys(Keys.TAB, Keys.TAB).perform()
                actions.key_down(Keys.CONTROL).send_keys("a").key_up(
                    Keys.CONTROL
                ).perform()
                actions.send_keys(search_location.strip()).perform()
                sleep(2)
                actions.send_keys(Keys.ENTER).perform()
                try_xp(driver, ".//button[@aria-label='Cancel']")
            except Exception as e:
                try_xp(driver, ".//button[@aria-label='Cancel']")
                print_lg(
                    "Failed to update search location, continuing with default location!",
                    e,
                )

    def scroll_to_view(
        self,
        driver: WebDriver,
        element: WebElement,
        top: bool = False,
        smooth_scroll: bool = False,
    ) -> None:
        if top:
            return driver.execute_script("arguments[0].scrollIntoView();", element)
        behavior = "smooth" if smooth_scroll else "instant"
        return driver.execute_script(
            'arguments[0].scrollIntoView({block: "center", behavior: "'
            + behavior
            + '" });',
            element,
        )

    def wait_span_click(
        self,
        driver: WebDriver,
        x: str,
        time: float = 5.0,
        click: bool = True,
        scroll: bool = True,
        scrollTop: bool = False,
    ) -> WebElement | bool:
        if x:
            try:
                button = WebDriverWait(driver, time).until(
                    EC.presence_of_element_located(
                        (By.XPATH, './/span[normalize-space(.)="' + x + '"]')
                    )
                )
                if scroll:
                    self.scroll_to_view(driver, button, scrollTop)
                if click:
                    button.click()
                    buffer(click_gap)
                return button
            except Exception as e:
                print_lg("Click Failed! Didn't find '" + x + "'")
                return False

    def multi_sel(self, driver: WebDriver, l: list, time: float = 5.0) -> None:
        for x in l:
            try:
                button = WebDriverWait(driver, time).until(
                    EC.presence_of_element_located(
                        (By.XPATH, './/span[normalize-space(.)="' + x + '"]')
                    )
                )
                self.scroll_to_view(driver, button)
                button.click()
                buffer(click_gap)
            except Exception as e:
                print_lg("Click Failed! Didn't find '" + x + "'")

    def multi_sel_noWait(
        self, driver: WebDriver, l: list, actions: bool = False
    ) -> None:
        for x in l:
            try:
                button = driver.find_element(
                    By.XPATH, './/span[normalize-space(.)="' + x + '"]'
                )
                self.scroll_to_view(driver, button)
                button.click()
                buffer(click_gap)
            except Exception as e:
                if actions:
                    self.company_search_click(driver, actions, x)
                else:
                    print_lg("Click Failed! Didn't find '" + x + "'")
                # print_lg(e)

    def boolean_button_click(self, driver: WebDriver, actions, x: str) -> None:
        try:
            list_container = driver.find_element(
                By.XPATH, './/h3[normalize-space()="' + x + '"]/ancestor::fieldset'
            )
            button = list_container.find_element(By.XPATH, './/input[@role="switch"]')
            self.scroll_to_view(driver, button)
            actions.move_to_element(button).click().perform()
            buffer(click_gap)
        except Exception as e:
            print_lg("Click Failed! Didn't find '" + x + "'")

    def get_job_main_details(self, job: WebElement) -> tuple[str, str, str, str, str]:
        """
        # Function to get job main details.
        Returns a tuple of (job_id, title, company, work_location, work_style, skip)
        * job_id: Job ID
        * title: Job title
        * company: Company name
        * work_location: Work location of this job
        * work_style: Work style of this job (Remote, On-site, Hybrid)
        * skip: A boolean flag to skip this job
        """

        job_details_button = job.find_element(
            By.CLASS_NAME, "job-card-list__title--link"
        )
        self.scroll_to_view(driver, job_details_button, True)
        title = job_details_button.text
        company = job.find_element(
            By.CLASS_NAME, "artdeco-entity-lockup__subtitle"
        ).text
        job_id = job.get_dom_attribute("data-occludable-job-id")
        work_location = job.find_element(
            By.CLASS_NAME, "artdeco-entity-lockup__caption"
        ).text
        work_style = work_location[
            work_location.rfind("(") + 1 : work_location.rfind(")")
        ]
        work_location = work_location[: work_location.rfind("(")].strip()

        try:
            job_details_button.click()
        except Exception as e:
            print_lg(
                f'Failed to click "{title} | {company}" job on details button. Job ID: {job_id}!'
            )
            print_lg(e)
        buffer(click_gap)

        return (job_id, title, company, work_location, work_style)

    def try_find_by_classes(
        self, driver: WebDriver, classes: list[str]
    ) -> WebElement | ValueError:
        for cla in classes:
            try:
                return driver.find_element(By.CLASS_NAME, cla)
            except:
                pass
        raise ValueError("Failed to find an element with given classes")

    def get_page_info(self) -> tuple[WebElement | None, int | None]:
        """
        Function to get pagination element and current page number
        """
        try:
            # pagination_element = self.try_find_by_classes(
            #     driver, ["jobs-search-pagination", "jobs-search-pagination__pages"]
            # )
            pagination_element = self.try_find_by_classes(
                driver,
                ["artdeco-pagination__pages", "artdeco-pagination__pages--number"],
            )
            print_lg(pagination_element)

            self.scroll_to_view(driver, pagination_element)

            # current_page = int(
            #     pagination_element.find_element(
            #         By.XPATH,
            #         "//button[contains(@class, 'jobs-search-pagination__indicator-button--active')]",
            #     ).text
            # )
            current_page = int(
                pagination_element.find_element(
                    By.XPATH, "//li[contains(@class, 'active')]"
                ).text
            )
            print_lg(current_page)

        except Exception as e:
            print_lg(
                "Failed to find Pagination element, hence couldn't scroll till end!"
            )
            pagination_element = None
            current_page = None
            print_lg(e)
        return pagination_element, current_page

    def apply_filters(self) -> None:
        """
        Function to apply job search filters
        """
        self.set_search_location()

        try:
            recommended_wait = 1 if click_gap < 1 else 0

            wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//button[normalize-space()="All filters"]')
                )
            ).click()
            buffer(recommended_wait)

            self.wait_span_click(driver, self.sort_by)
            self.wait_span_click(driver, self.date_posted)
            buffer(recommended_wait)

            self.multi_sel(driver, self.experience_level)
            self.multi_sel_noWait(driver, [], actions)
            if self.experience_level or []:
                buffer(recommended_wait)

            self.multi_sel(driver, self.job_type)
            self.multi_sel(driver, self.on_site)
            if self.job_type or self.on_site:
                buffer(recommended_wait)

            self.multi_sel_noWait(driver, self.location)
            self.multi_sel_noWait(driver, self.industry)
            if self.location or self.industry:
                buffer(recommended_wait)

            self.multi_sel_noWait(driver, self.job_function)
            self.multi_sel_noWait(driver, self.job_titles)
            if self.job_function or self.job_titles:
                buffer(recommended_wait)

            show_results_button: WebElement = driver.find_element(
                By.XPATH,
                '//button[contains(@aria-label, "Apply current filters to show")]',
            )
            show_results_button.click()

        except Exception as e:
            print_lg("Setting the preferences failed!")
            # print_lg(e)

    def search(self, search_terms: list[str]) -> None:
        for searchTerm in search_terms:
            driver.get(f"https://www.linkedin.com/jobs/search/?keywords={searchTerm}")
            print_lg(
                "\n________________________________________________________________________________________________________________________\n"
            )
            print_lg(f'\n>>>> Now searching for "{searchTerm}" <<<<\n\n')

            self.apply_filters()

            current_count = 0
            try:
                while current_count < switch_number:
                    # Wait until job listings are loaded
                    # wait.until(EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@class, 'jobs-card-list')]")))
                    wait.until(
                        EC.presence_of_all_elements_located(
                            (
                                By.XPATH,
                                "//li[contains(@class, 'scaffold-layout__list-item')]",
                            )
                        )
                    )

                    pagination_element, current_page = self.get_page_info()
                    print_lg(f"\n>-> Now on Page {current_page} \n")

                    # Find all job listings in current page
                    buffer(3)
                    # job_listings = driver.find_elements(By.CLASS_NAME, "jobs-search-results__list-item")
                    job_listings = driver.find_elements(
                        By.CLASS_NAME, "scaffold-layout__list-item"
                    )

                    for job in job_listings:
                        if keep_screen_awake:
                            pyautogui.press("shiftright")
                        if current_count >= switch_number:
                            break
                        print_lg("\n-@-\n")

                        job_id, title, company, work_location, work_style = (
                            self.get_job_main_details(job)
                        )

                        job_link = "https://www.linkedin.com/jobs/view/" + job_id
                        application_link = "Easy Applied"
                        date_applied = "Pending"
                        hr_link = "Unknown"
                        hr_name = "Unknown"
                        connect_request = "In Development"  # Still in development
                        date_listed = "Unknown"
                        description = "Unknown"
                        experience_required = "Unknown"
                        skills = "In Development"  # Still in development
                        resume = "Pending"
                        reposted = False
                        questions_list = None
                        screenshot_name = "Not Available"

                        # Get job description
                        try:
                            description = self.find_by_class(
                                driver, "jobs-box__html-content"
                            ).text

                        except Exception as e:
                            if description == "Unknown":
                                print_lg("Unable to extract job description!")

                        print_lg(
                            f"""Successfully saved "{title} | {company}" job. Job ID: {job_id} info
                            \n-@-\n
                            {title} | {company} | {work_location} | {work_style} | {description}"""
                        )
                        current_count += 1

                    # Switching to next page
                    if pagination_element == None:
                        print_lg(
                            "Couldn't find pagination element, probably at the end page of results!"
                        )
                        break
                    try:
                        pagination_element.find_element(
                            By.XPATH, f"//button[@aria-label='Page {current_page+1}']"
                        ).click()
                        print_lg(f"\n>-> Now on Page {current_page+1} \n")
                    except NoSuchElementException:
                        print_lg(
                            f"\n>-> Didn't find Page {current_page+1}. Probably at the end page of results!\n"
                        )
                        break

            except Exception as e:
                print_lg("Failed to find Job listings!")
                critical_error_log("In Applier", e)
