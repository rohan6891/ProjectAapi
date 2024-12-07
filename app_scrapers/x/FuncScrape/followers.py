from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import time
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from FuncScrape.pdf_utils import create_title_page, scale_image
import os

def fetch_followers(driver, pdf_report, username, f_upath):
    driver.get(f"https://x.com/{username}/followers")
    time.sleep(5)
    path = os.path.join(f_upath, "Followers")
    os.makedirs(path, exist_ok=True)
    create_title_page(pdf_report, "FOLLOWERS")
    # Add title page for chats
    width, height = A4
    followers_section = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="primaryColumn"]'))
    )

    current_position = 0
    scroll_offset = driver.execute_script("return window.innerHeight;")  # Scroll by the visible window height
    total_height = driver.execute_script("return arguments[0].scrollHeight;", followers_section)

    print("Starting capture of followers...")

    while current_position < total_height:
        # Take a screenshot of the current view
        screenshot_path = os.path.join(path, f"followers_{current_position}.png")
        driver.save_screenshot(screenshot_path)

        # Add the screenshot to the PDF
        img = Image.open(screenshot_path)
        img_pdf_width, img_pdf_height = scale_image(img, width - 2 * 30, height - 2 * 30)
        x = (width - img_pdf_width) / 2
        y = (height - img_pdf_height) / 2
        pdf_report.drawImage(screenshot_path, x, y, width=img_pdf_width, height=img_pdf_height)
        pdf_report.showPage()

        # Scroll down by the offset
        current_position += scroll_offset
        driver.execute_script(f"window.scrollTo(0, {current_position});")
        time.sleep(2)  # Allow the content to load

        # Recalculate the total height (in case it changes due to lazy loading)
        total_height = driver.execute_script("return arguments[0].scrollHeight;", followers_section)

    print("Finished capturing followers.")
