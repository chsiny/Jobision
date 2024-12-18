from config import logs_folder_path
from datetime import datetime
from time import sleep
from random import randint
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os


def make_directories(paths: list[str]) -> None:
    """
    Function to create missing directories
    """
    for path in paths:
        path = path.replace("//", "/")
        if "/" in path and "." in path:
            path = path[: path.rfind("/")]
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except Exception as e:
            print(f'Error while creating directory "{path}": ', e)


def find_default_profile_directory() -> str | None:
    """
    Function to search for Chrome Profiles within default locations
    """
    default_locations = [
        r"%LOCALAPPDATA%\Google\Chrome\User Data",
        r"%USERPROFILE%\AppData\Local\Google\Chrome\User Data",
        r"%USERPROFILE%\Local Settings\Application Data\Google\Chrome\User Data",
    ]
    for location in default_locations:
        profile_dir = os.path.expandvars(location)
        if os.path.exists(profile_dir):
            return profile_dir
    return None


def critical_error_log(possible_reason: str, stack_trace: Exception) -> None:
    """
    Function to log and print critical errors along with datetime stamp
    """
    print_lg(possible_reason, stack_trace, datetime.now())


def print_lg(*msgs: str) -> None:
    """
    Function to log and print
    """
    try:
        message = "\n".join(str(msg) for msg in msgs)
        path = logs_folder_path + "/log.txt"
        with open(path.replace("//", "/"), "a+", encoding="utf-8") as file:
            file.write(message + "\n")
        print(message)
    except Exception as e:
        critical_error_log("Log.txt is open or is occupied by another program!", e)


def buffer(speed: int = 0) -> None:
    """
    Function to wait within a period of selected random range.
    * Will not wait if input `speed <= 0`
    * Will wait within a random range of
      - `0.6 to 1.0 secs` if `1 <= speed < 2`
      - `1.0 to 1.8 secs` if `2 <= speed < 3`
      - `1.8 to speed secs` if `3 <= speed`
    """
    if speed <= 0:
        return
    elif speed <= 1 and speed < 2:
        return sleep(randint(6, 10) * 0.1)
    elif speed <= 2 and speed < 3:
        return sleep(randint(10, 18) * 0.1)
    else:
        return sleep(randint(18, round(speed) * 10) * 0.1)

def try_xp(driver: WebDriver, xpath: str, click: bool = True) -> WebElement | bool:
    try:
        if click:
            driver.find_element(By.XPATH, xpath).click()
            return True
        else:
            return driver.find_element(By.XPATH, xpath)
    except:
        return False
    
def try_linkText(driver: WebDriver, linkText: str) -> WebElement | bool:
    try:
        return driver.find_element(By.LINK_TEXT, linkText)
    except:
        return False
    
def text_input_by_ID(driver: WebDriver, id: str, value: str, time: float = 5.0) -> None:
    username_field = WebDriverWait(driver, time).until(
        EC.presence_of_element_located((By.ID, id))
    )
    username_field.send_keys(Keys.CONTROL + "a")
    username_field.send_keys(value)
    
def text_input(
    actions: ActionChains,
    textInputEle: WebElement | bool,
    value: str,
    textFieldName: str = "Text",
) -> None | Exception:
    if textInputEle:
        sleep(1)
        # actions.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).perform()
        textInputEle.clear()
        textInputEle.send_keys(value.strip())
        sleep(2)
        actions.send_keys(Keys.ENTER).perform()
    else:
        print_lg(f"{textFieldName} input was not given!")

