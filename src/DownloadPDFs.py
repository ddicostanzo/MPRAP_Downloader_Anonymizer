import os
import time
import argparse
import warnings

from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

DOWNLOAD_PATH = r""
MPRAP_URL = r'https://mprap.aapm.org/login'
LOGIN_ID = "" # email address for login information
LOGIN_PASS = "" # password for login information
APPLICATION_ID = '' # application ID, see the URL when logging in manually


def downloads_done() -> None:
    """
    Checks if the downloads have completed in the folder. If not, sleep for 5 secs and check again.
    """
    path = DOWNLOAD_PATH
    for i in os.listdir(path):
        if ".crdownload" in i:
            time.sleep(5)
            downloads_done()


def main():
    # Create the download path if it doesn't exist
    if not os.path.exists(DOWNLOAD_PATH):
        os.mkdir(DOWNLOAD_PATH)

    # Set up the options for the download path and always open PDFs externally
    # If your center uses Group Policy to enforce items in Chrome, this may take a minor registry
    # change to work
    options = Options()
    options.add_argument("start-maximized")
    profile = {
        "download.default_directory": DOWNLOAD_PATH,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True
    }

    options.add_experimental_option("prefs", profile)

    # Open Chrome
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(MPRAP_URL)

    # Login to the website
    username = driver.find_element(By.NAME, "email")
    username.send_keys(LOGIN_ID)
    password = driver.find_element(By.NAME, "password")
    password.send_keys(LOGIN_PASS)
    button = driver.find_element(By.CSS_SELECTOR, ".btn-primary")
    time.sleep(2)
    button.send_keys(Keys.RETURN)

    # Go to the Applications page
    driver.get(r'https://mprap.aapm.org/institutions/applicants')
    driver.get(r'https://mprap.aapm.org/institutions/applicants/' + APPLICATION_ID)

    # Find the application table
    applicant_table = driver.find_element(By.ID, "applicantList")
    apps = applicant_table.find_elements(By.TAG_NAME, "tr")

    # For each application, download it
    for app in apps:
        if len(app.find_elements(By.TAG_NAME, "td")) > 0:
            col = app.find_elements(By.TAG_NAME, "td")[0]
            link = col.find_element(By.TAG_NAME, "a")
            print(col.text)
            link.click()
            time.sleep(3)
            driver.switch_to.window(driver.window_handles[0])

            downloads_done()
        else:
            continue

    driver.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--download_directory', type=str,
                        help='The directory where to download the applications to.')
    parser.add_argument('--url', type=str, help='If the MPRAP website changes, this will need to be modified, '
                                                'otherwise leave this argument blank.')
    parser.add_argument('-u', '--userid', type=str, help='Login ID for MPRAP system')
    parser.add_argument('-p', '--password', type=str, help='Password for MPRAP system')
    parser.add_argument('-a', '--application_id', type=str,
                        help='The application ID that identifies the current year and program. Can be found when '
                             'manually logging into the system as part of the URL')
    args = parser.parse_args()

    if args.download_directory is None:
        assert SyntaxError('The download directory is a required argument.')
        exit()

    if args.userid is None:
        assert SyntaxError('The MPRAP user id is a required argument.')
        exit()

    if args.password is None:
        assert SyntaxError('The MPRAP password is a required argument.')
        exit()

    if args.application_id is None:
        assert SyntaxError('The application id is a required argument.')
        exit()

    DOWNLOAD_PATH = args.download_directory
    LOGIN_ID = args.userid
    LOGIN_PASS = args.password
    APPLICATION_ID = args.application_id

    if args.url is not None:
        warnings.warn('Manually setting the MPRAP website URL because it was provided')
        MPRAP_URL = args.url

    exit(main())
