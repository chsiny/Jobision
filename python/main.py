# python/main.py
from scrapers.linkedin_scraper import LinkedInScraper
from analyzer.analyzer import JobAnalyzer
from utils.open_chrome import *

def main():
    scraper = LinkedInScraper()
    driver.get("https://www.linkedin.com/login")
    if not scraper.is_logged_in(): scraper.login()

    linkedIn_tab = driver.current_window_handle

    driver.switch_to.window(linkedIn_tab)
    
    # test linkedin_scraper.py funcitons
    jobs = scraper.search(["Software Engineer"])
    print(jobs)

if __name__ == "__main__":
    main()
