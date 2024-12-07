import os
import time
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app_scrapers.instagram.FuncScrape.pdf_utils import create_title_page, scale_image

def fetch_likes(driver, pdf_report,f_upath ):
    """Fetches liked posts from Instagram and adds them to the PDF report."""
    likes_url = "https://www.instagram.com/your_activity/interactions/likes"  # Update this URL if needed
    driver.get(likes_url)
    time.sleep(6)

    # Create directory for saving screenshots
    path = os.path.join(f_upath, "Likes")
    os.makedirs(path, exist_ok=True)
    create_title_page(pdf_report, "LIKED POSTS")
    # Initialize variable to keep track of the number of screenshots taken
    screenshot_index = 0

    # Take an initial screenshot before trying to find the scrollable div
    screenshot_path = os.path.join(path, f"likes_screenshot_{screenshot_index}.png")
    driver.save_screenshot(screenshot_path)
    print(f"Initial screenshot saved at: {screenshot_path}")
    screenshot_index += 1

    # Scroll and take screenshots of likes in a loop
    try:
        scrollable_div = driver.find_element(By.XPATH, '//div[@data-blocks-name="bk.components.Collection"]')

        while True:
            # Take a screenshot of the Likes overview page
            screenshot_path = os.path.join(path, f"likes_screenshot_{screenshot_index}.png")
            driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved at: {screenshot_path}")
            screenshot_index += 1

            # Scroll down to load more likes
            prev_scroll_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
            driver.execute_script("arguments[0].scrollTop += arguments[0].clientHeight", scrollable_div)
            time.sleep(3)  # Wait for loading more likes

            # Check if we have reached the end of the scrollable content
            new_scroll_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
            if new_scroll_height == prev_scroll_height:
                print("Reached the end of the likes.")
                break

    except Exception as e:
        print(f"Error while scrolling and taking screenshots: {e}")

    
    width, height = A4
    margin = 30
    

    # Add all screenshots to the PDF
    for i in range(screenshot_index):
        img_path = os.path.join(path, f"likes_screenshot_{i}.png")
        img = Image.open(img_path)
        img_pdf_width, img_pdf_height = scale_image(img, width - 2 * margin, height - 2 * margin)
        x = (width - img_pdf_width) / 2
        y = (height - img_pdf_height) / 2
        pdf_report.drawImage(img_path, x, y, width=img_pdf_width, height=img_pdf_height)
        pdf_report.showPage()
