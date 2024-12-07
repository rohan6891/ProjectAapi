import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from app_scrapers.instagram.FuncScrape.pdf_utils import create_title_page, scale_image

def fetch_following(driver, pdf_report, username, f_upath):
    """Fetches following from Instagram and adds them to the PDF report."""
    profile_url = f"https://www.instagram.com/{username}/"
    driver.get(profile_url)
    time.sleep(6)

    # Locate and click the following link
    try:
        following_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//a[@href='/{username}/following/']"))
        )
        following_link.click()
        print("Navigated to following page.")
    except Exception as e:
        print(f"Error locating following link: {e}")
        return

    # Wait for the following modal to load
    time.sleep(3)

    # Create directory to save screenshots
    path = os.path.join(f_upath, "Following")
    os.makedirs(path, exist_ok=True)

    # Add a title page to the PDF
    create_title_page(pdf_report, "FOLLOWING")

    # Define scrolling container and following div class
    scrolling_div_xpath = "//div[contains(@class, 'xyi19xy x1ccrb07 xtf3nb5 x1pc53ja x1lliihq x1iyjqo2 xs83m0k xz65tgg x1rife3k x1n2onr6')]"

    try:
        scrolling_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, scrolling_div_xpath))
        )
    except Exception as e:
        print(f"Error locating scrolling container: {e}")
        return

    margin = 30
    width, height = pdf_report._pagesize  # Retrieve the current page dimensions
    screenshot_counter = 1
    previous_scroll_position = 0
    scroll_increment = 300

    while True:
        try:
            # Take a screenshot of the viewport
            screenshot_path = os.path.join(path, f"following_{screenshot_counter}.png")
            driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved: {screenshot_path}")

            # Open the screenshot to scale it
            img = Image.open(screenshot_path)
            img_pdf_width, img_pdf_height = scale_image(img, width - 2 * margin, height - 2 * margin)

            # Add the scaled image to the PDF
            x = (width - img_pdf_width) / 2
            y = (height - img_pdf_height) / 2
            pdf_report.drawImage(screenshot_path, x, y, width=img_pdf_width, height=img_pdf_height)
            pdf_report.showPage()
            screenshot_counter += 1

            # Check for 'Suggested for you' span
            try:
                suggested_span = driver.find_element(By.XPATH, "//span[text()='Suggested for you']")
                print("Found 'Suggested for you'. Stopping.")
                break
            except Exception:
                print("'Suggested for you' not found. Scrolling...")

            # Scroll the div incrementally
            driver.execute_script("arguments[0].scrollTop += arguments[1];", scrolling_div, scroll_increment)
            time.sleep(5)  # Pause to allow new content to load

            # Check if the scroll position has reached the bottom
            current_scroll_position = driver.execute_script("return arguments[0].scrollTop;", scrolling_div)
            if current_scroll_position == previous_scroll_position:
                print("Reached the bottom of the list. Stopping.")
                break
            previous_scroll_position = current_scroll_position

        except Exception as e:
            print(f"Error during scrolling or processing: {e}")
            break
