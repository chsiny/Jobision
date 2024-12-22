# python/main.py
from scrapers.linkedin_scraper import LinkedInScraper
from analyzer.analyzer import JobAnalyzer
from utils.open_chrome import *
from utils.filter import Filter


def main():
    filter = Filter(search_terms=["Software Engineer"], search_location="Australia")
    scraper = LinkedInScraper(driver, filter)
    if not scraper.is_logged_in():
        scraper.login()

    linkedIn_tab = scraper.driver.current_window_handle
    scraper.driver.switch_to.window(linkedIn_tab)

    # test linkedin_scraper.py funcitons
    scraper.search()


if __name__ == "__main__":
    main()
