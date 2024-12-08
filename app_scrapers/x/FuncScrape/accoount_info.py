from selenium.webdriver.common.by import By
from PIL import Image
import time
from reportlab.lib.pagesizes import A4
from app_scrapers.x.FuncScrape.pdf_utils import create_title_page, scale_image
import os
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException


def fetch_account_details(driver, pdf_report, output_path, password):
    # Create a folder for Twitter/X Account Details
    path = os.path.join(output_path, "Account_Details")
    os.makedirs(path, exist_ok=True)

    # Add a title page for the PDF
    create_title_page(pdf_report, "TWITTER/X ACCOUNT DETAILS")
    width, height = A4

    try:
        # Navigate to the Account Settings page
        driver.get("https://x.com/settings/account")
        print("Navigating to Twitter/X account settings...")
        time.sleep(5)

        # Locate and click on the "Your Twitter Data" link
        twitter_data_link = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href="/settings/your_twitter_data/account"]'))
        )
        twitter_data_link.click()
        print("Clicked on 'Your Twitter Data' link.")
        time.sleep(5)

        # Locate the password input field and enter the password
        password_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"]'))
        )
        password_input.send_keys(password)
        print("Entered password.")

        # Locate and click the "Confirm" button
        confirm_button = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.XPATH, '//span[contains(text(), "Confirm")]/ancestor::button')
            )
        )
        confirm_button.click()
        print("Clicked on 'Confirm' button.")
        time.sleep(5)

        # Take a screenshot of the account details page
        screenshot_path = os.path.join(path, "account_details.png")
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved at: {screenshot_path}")

        # Add the screenshot to the PDF
        img = Image.open(screenshot_path)
        img_pdf_width, img_pdf_height = scale_image(img, width - 60, height - 60)  # 30 margin on all sides
        x = (width - img_pdf_width) / 2
        y = (height - img_pdf_height) / 2
        pdf_report.drawImage(screenshot_path, x, y, width=img_pdf_width, height=img_pdf_height)
        pdf_report.showPage()

        print("Account details added to the PDF.")
    except TimeoutException:
        print("Timeout occurred while navigating to or interacting with the page.")
    except Exception as e:
        print(f"An error occurred: {e}")
