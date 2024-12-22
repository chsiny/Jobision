# python/scrapers/linkedin_scraper.py
from scrapers.base_scraper import BaseScraper
from utils.helpers import *
from config import *
from utils.open_chrome import *
from utils.filter import *
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
    StaleElementReferenceException,
)
from selenium.webdriver.common.action_chains import ActionChains
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

    def __init__(self, driver: WebDriver, filter: Filter) -> None:
        super().__init__("https://www.linkedin.com/jobs")
        self.driver = driver
        self.filter = filter

    def is_logged_in(self) -> bool:
        self.driver.get("https://www.linkedin.com/login")
        if self.driver.current_url == "https://www.linkedin.com/feed/":
            return True
        if try_linkText(self.driver, "Sign in"):
            return False
        if try_xp(
            self.driver, '//button[@type="submit" and contains(text(), "Sign in")]'
        ):
            return False
        if try_linkText(self.driver, "Join now"):
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
        self.driver.get("https://www.linkedin.com/login")
        try:
            wait.until(
                EC.presence_of_element_located((By.LINK_TEXT, "Forgot password?"))
            )
            try:
                text_input_by_ID(self.driver, "username", username, 1)
            except Exception as e:
                print_lg("Couldn't find username field.")
                # print_lg(e)
            try:
                text_input_by_ID(self.driver, "password", password, 1)
            except Exception as e:
                print_lg("Couldn't find password field.")
                # print_lg(e)
            # Find the login submit button and click it
            self.driver.find_element(
                By.XPATH, '//button[@type="submit" and contains(text(), "Sign in")]'
            ).click()
        except Exception:
            try:
                profile_button = self.find_by_class(self.driver, "profile__details")
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
            self.manual_login_retry(self.is_logged_in, 2)

    def manual_login_retry(self, is_logged_in: callable, limit: int = 2) -> None:
        """
        Function to ask and validate manual login
        """
        count = 0
        while not is_logged_in():
            from pyautogui import alert

            print_lg("Seems like you're not logged in!")
            button = "Confirm Login"
            message = (
                'After you successfully Log In, please click "{}" button below.'.format(
                    button
                )
            )
            if count > limit:
                button = "Skip Confirmation"
                message = 'If you\'re seeing this message even after you logged in, Click "{}". Seems like auto login confirmation failed!'.format(
                    button
                )
            count += 1
            if alert(message, "Login Required", button) and count > limit:
                return

    # Find functions
    def find_by_class(
        self, class_name: str, time: float = 5.0
    ) -> WebElement | Exception:
        return WebDriverWait(self.driver, time).until(
            EC.presence_of_element_located((By.CLASS_NAME, class_name))
        )

    def set_search_location(self) -> None:
        """
        Function to set search location
        """
        if self.filter.get_search_location().strip():
            try:
                print_lg(
                    f'Setting search location as: "{self.filter.get_search_location().strip()}"'
                )
                search_location_ele = try_xp(
                    self.driver,
                    ".//input[@aria-label='City, state, or zip code'and not(@disabled)]",
                    False,
                )  #  and not(@aria-hidden='true')]")
                text_input(
                    actions,
                    search_location_ele,
                    self.filter.get_search_location(),
                    "Search Location",
                )
            except ElementNotInteractableException:
                try_xp(
                    self.driver,
                    ".//label[@class='jobs-search-box__input-icon jobs-search-box__keywords-label']",
                )
                actions.send_keys(Keys.TAB, Keys.TAB).perform()
                actions.key_down(Keys.CONTROL).send_keys("a").key_up(
                    Keys.CONTROL
                ).perform()
                actions.send_keys(search_location.strip()).perform()
                sleep(2)
                actions.send_keys(Keys.ENTER).perform()
                try_xp(self.driver, ".//button[@aria-label='Cancel']")
            except Exception as e:
                try_xp(self.driver, ".//button[@aria-label='Cancel']")
                print_lg(
                    "Failed to update search location, continuing with default location!",
                    e,
                )

    def scroll_to_view(
        self,
        element: WebElement,
        top: bool = False,
        smooth_scroll: bool = False,
    ) -> None:
        if top:
            return self.driver.execute_script("arguments[0].scrollIntoView();", element)
        behavior = "smooth" if smooth_scroll else "instant"
        return self.driver.execute_script(
            'arguments[0].scrollIntoView({block: "center", behavior: "'
            + behavior
            + '" });',
            element,
        )

    def wait_span_click(
        self,
        x: str,
        time: float = 10.0,
        click: bool = True,
        scroll: bool = True,
        scrollTop: bool = False,
        retries: int = 3,
    ) -> WebElement | bool:
        if x:
            for attempt in range(retries):
                try:
                    button = WebDriverWait(self.driver, time).until(
                        EC.presence_of_element_located(
                            (By.XPATH, f'//span[normalize-space(.)="{x}"]')
                        )
                    )
                    if scroll:
                        self.scroll_to_view(button, scrollTop)
                    if click:
                        actions = ActionChains(self.driver)
                        actions.move_to_element(button).click_and_hold(button).pause(
                            1
                        ).release(button).perform()
                        buffer(click_gap)
                    else:
                        return button
                except Exception as e:
                    print_lg(f"Attempt {attempt + 1}: Click Failed! Didn't find '{x}'")
                    print_lg(e)
            return False
        return False

    def multi_sel(self, l: list, time: float = 5.0) -> None:
        for x in l:
            try:
                button = WebDriverWait(self.driver, time).until(
                    EC.presence_of_element_located(
                        (By.XPATH, './/span[normalize-space(.)="' + x + '"]')
                    )
                )
                self.scroll_to_view(button)
                button.click()
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
        self.scroll_to_view(job_details_button, True)
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

    def try_find_by_classes(self, classes: list[str]) -> WebElement | ValueError:
        for cla in classes:
            try:
                return self.driver.find_element(By.CLASS_NAME, cla)
            except:
                pass
        raise ValueError("Failed to find an element with given classes")

    def get_page_info(self) -> tuple[WebElement | None, int | None]:
        """
        Function to get pagination element and current page number
        """
        try:
            pagination_element = self.try_find_by_classes(
                ["artdeco-pagination__pages", "artdeco-pagination__pages--number"],
            )
            print_lg(pagination_element)

            self.scroll_to_view(pagination_element)

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

    def find_largest_pagination_number(self) -> int:
        pagination_elements = self.driver.find_elements(
            By.CLASS_NAME, "artdeco-pagination__indicator--number"
        )
        if not pagination_elements:
            print_lg("Couldn't find pagination elements!")
            return 0

        print_lg(f"Found {len(pagination_elements)} pagination elements")

        # Assuming the pagination elements are sorted in ascending order
        last_element = pagination_elements[-1]
        page_number = last_element.get_attribute("data-test-pagination-page-btn")
        if page_number and page_number.isdigit():
            largest_page_number = int(page_number)
            return largest_page_number
        else:
            print_lg("Couldn't extract page number from the last pagination element!")
            return 0

    def apply_filters(self) -> None:
        """
        Applies job search filters on LinkedIn.

        This function sets the search location and applies various job search filters
        such as sort by, date posted, experience level, job type, on-site/remote,
        location, industry, job function, and job title. It then clicks the button
        to apply the current filters and show the results.

        Raises:
            Exception: If setting the preferences fails.
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

            self.wait_span_click(self.filter.get_sort_by())
            self.wait_span_click(self.filter.get_date_posted())
            buffer(10)

            try:
                show_results_button = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            '//button[@data-test-reusables-filters-modal-show-results-button="true"]',
                        )
                    )
                )
                show_results_button.click()
                buffer(10)
            except Exception as e:
                print_lg("Couldn't find 'Show results' button!")
                # print_lg(e)

        except Exception as e:
            print_lg("Setting the preferences failed!")
            # print_lg(e)

    def search(self) -> None:
        """
        Function to search for jobs on LinkedIn based on search terms and apply filters.

        This function performs the following steps:
        1. Iterates over search terms obtained from the filter.
        2. Navigates to the LinkedIn job search page for each search term.
        3. Applies the specified filters to the search results.
        4. Determines the total number of pages of search results.
        5. Iterates through each page of search results and extracts job listings.
        6. For each job listing, extracts job details such as job ID, title, company, work location, and work style.
        7. Attempts to extract the job description.
        8. Logs the extracted job details.
        9. Navigates to the next page of search results until the end of the results is reached.

        Raises:
            Exception: If unable to extract job description or find job listings.
            NoSuchElementException: If unable to find the pagination element for the next page.
        """
        for searchTerm in self.filter.get_search_terms():
            driver.get(f"https://www.linkedin.com/jobs/search/?keywords={searchTerm}")
            print_lg(f'\n>>>> Now searching for "{searchTerm}" <<<<\n\n')

            self.apply_filters()

            total_page = self.find_largest_pagination_number()

            print_lg(f"\n>-> Total pages {total_page} \n")

            for _ in range(total_page):
                # Wait until job listings are loaded
                wait.until(
                    EC.presence_of_all_elements_located(
                        (
                            By.XPATH,
                            "//li[contains(@class, 'scaffold-layout__list-item')]",
                        )
                    )
                )

                pagination_element, current_page = self.get_page_info()

                # Find all job listings in current page
                buffer(3)

                try:
                    job_listings = self.driver.find_elements(
                        By.CLASS_NAME, "scaffold-layout__list-item"
                    )

                    for job in job_listings:
                        if keep_screen_awake:
                            pyautogui.press("shiftright")
                        print_lg("\n-@-\n")

                        job_id, title, company, work_location, work_style = (
                            self.get_job_main_details(job)
                        )
                        buffer(2)

                        # Get job description
                        try:
                            description = self.find_by_class(
                                "jobs-box__html-content"
                            ).text

                        except Exception as e:
                            if description == "Unknown":
                                print_lg("Unable to extract job description!")

                        print_lg(
                            f"""Successfully saved "{title} | {company}" job. Job ID: {job_id}\n
                            {work_location} | {work_style}"""
                        )
                except Exception as e:
                    print_lg("Failed to find Job listings!")

                # Switching to next page
                if pagination_element == None:
                    print_lg(
                        "Couldn't find pagination element, probably at the end page of results!"
                    )
                    break
                try:
                    pagination_element.find_element(
                        By.XPATH, f"//button[@aria-label='Page {current_page + 1}']"
                    ).click()
                    print_lg(f"\n>-> Now on Page {current_page + 1} \n")
                except NoSuchElementException:
                    print_lg(
                        f"\n>-> Didn't find Page {current_page + 1}. Probably at the end page of results!\n"
                    )
                    break

    def __str__(self):
        return f"LinkedInScraper(driver={self.driver}, filter={self.filter})"

    def __repr__(self):
        return f"LinkedInScraper(driver={self.driver}, filter={self.filter})"

    def set_filter(self, filter: Filter):
        self.filter = filter

    def get_filter(self) -> Filter:
        return self.filter

    def set_driver(self, driver: WebDriver):
        self.driver = driver

    def get_driver(self) -> WebDriver:
        return self.driver

    def set_url(self, url: str):
        self.url = url

    def get_url(self) -> str:
        return self.url

    # Write a function to store job details in database
    def store_job_details(
        self,
        job_id: str,
        title: str,
        company: str,
        work_location: str,
        work_style: str,
        description: str,
    ) -> None:
        pass
