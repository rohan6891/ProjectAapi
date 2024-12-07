import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PIL import Image
from FuncScrape.pdf_utils import create_title_page, scale_image



def fetch_friends(driver, pdf_report, output_path):
    """
    Fetches the friends list from Facebook and adds screenshots of each friend's profile to a PDF.
    
    Args:
        driver: Selenium WebDriver instance.
        pdf_report: ReportLab PDF canvas object for adding pages.
        output_path: Directory path to save screenshots and PDF.
    """
    # Navigate to the friends list page
    friends_url = "https://www.facebook.com/friends/list"
    driver.get(friends_url)
    time.sleep(5)

    # Locate the "All friends" container
    try:
        all_friends_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@aria-label='All friends']"))
        )
        print("Located 'All friends' container.")
    except Exception as e:
        print(f"Error locating 'All friends' container: {e}")
        return

    # Create directory for saving screenshots
    screenshots_path = os.path.join(output_path, "Friends")
    os.makedirs(screenshots_path, exist_ok=True)
    create_title_page(pdf_report, "FACEBOOK FRIENDS LIST")

    width, height = A4
    margin = 30
    friend_index = 1

    # Find all anchor tags within the "All friends" div
    try:
        friend_links = all_friends_container.find_elements(By.TAG_NAME, "a")
        if len(friend_links) <= 2:
            print("No friends found beyond the first two links. Exiting.")
            return

        # Skip the first two anchor tags
        friend_links = friend_links[2:]
        print(f"Number of friends found: {len(friend_links)}")

        # Iterate through each friend's link
        for link in friend_links:
            try:
                # Open the friend's profile
                link.click()
                time.sleep(3)

                # Take screenshot
                screenshot_path = os.path.join(screenshots_path, f"friend_{friend_index}.png")
                driver.save_screenshot(screenshot_path)
                print(f"Saved screenshot: {screenshot_path}")

                # Add to PDF
                img = Image.open(screenshot_path)
                img_pdf_width, img_pdf_height = scale_image(img, width - 2 * margin, height - 2 * margin)
                x = (width - img_pdf_width) / 2
                y = (height - img_pdf_height) / 2
                pdf_report.drawImage(screenshot_path, x, y, width=img_pdf_width, height=img_pdf_height)
                pdf_report.showPage()

                # Return to the friends list
                driver.back()
                time.sleep(2)
            except Exception as e:
                print(f"Error processing friend link: {e}")
                continue

            friend_index += 1

    except Exception as e:
        print(f"Error locating or processing friend links: {e}")

    print("Finished capturing Facebook friends list.")
