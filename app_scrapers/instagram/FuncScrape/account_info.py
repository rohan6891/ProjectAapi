import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from app_scrapers.instagram.FuncScrape.pdf_utils import create_title_page, scale_image
from reportlab.lib.pagesizes import A4

def fetch_account_info(driver, pdf_report, username, f_upath):
    """
    Fetches account information from Instagram and adds screenshots to the PDF report.
    Args:
        driver: Selenium WebDriver instance.
        pdf_report: ReportLab Canvas instance for generating the PDF report.
        username: Instagram username for navigating to the profile.
        f_upath: Path to save screenshots and temporary files.
    """
    profile_url = f"https://www.instagram.com/{username}/"
    driver.get(profile_url)
    time.sleep(6)

    # Navigate to the accounts center URL
    accounts_center_url = "https://accountscenter.instagram.com/personal_info/"
    driver.get(accounts_center_url)
    time.sleep(6)

    screenshots_path = os.path.join(f_upath, "AccountInfo")
    os.makedirs(screenshots_path, exist_ok=True)

    # Add title page to the PDF
    create_title_page(pdf_report, "Account Information")

    # Define the sections to capture and their respective href suffix values
    sections = [
        {"name": "Contact Points", "href_suffix": "/contact_points/"},
        {"name": "Birthday", "href_suffix": "/personal_info/birthday/?entrypoint=accounts_center"}
    ]

    width, height = A4
    margin = 30

    for section in sections:
        try:
            # Find the anchor tag with the specific href suffix
            anchor_tag = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//a[contains(@href, '{section['href_suffix']}')]"))
            )
            anchor_tag.click()
            time.sleep(4)

            # Take a screenshot
            screenshot_path = os.path.join(screenshots_path, f"{section['name'].replace(' ', '_')}.png")
            driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved for {section['name']}.")

            # Add screenshot to the PDF
            img = Image.open(screenshot_path)
            img_pdf_width, img_pdf_height = scale_image(img, width - 2 * margin, height - 2 * margin)
            x = (width - img_pdf_width) / 2
            y = (height - img_pdf_height) / 2
            pdf_report.drawImage(screenshot_path, x, y, width=img_pdf_width, height=img_pdf_height)
            pdf_report.showPage()

            # Navigate back to the accounts center page
            driver.get(accounts_center_url)
            time.sleep(4)
        except Exception as e:
            print(f"Error capturing {section['name']}: {e}")
            continue

    print("Account information screenshots added to the PDF.")
