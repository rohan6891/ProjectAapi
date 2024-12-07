from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from reportlab.lib.pagesizes import A4
import os
import time

def fetch_chats(driver, pdf_report, output_path):
    """
    Scrolls to the top of each Instagram chat and captures screenshots of the chats,
    saving them as images and adding them to the provided PDF report.

    Args:
        driver: Selenium WebDriver instance.
        pdf_report: ReportLab canvas instance for adding chats to the PDF.
        output_path: Directory path to save chat screenshots.
    """
    driver.get('https://www.instagram.com/direct/inbox/')
    time.sleep(10)

    # Handle potential pop-ups
    try:
        alert = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Not Now")]'))
        )
        alert.click()
    except Exception:
        print("No initial pop-up found.")

    # Locate all chat contacts
    try:
        contacts = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[role="listitem"]'))
        )
        print(f"Found {len(contacts)} contacts.")
    except Exception as e:
        print(f"Error locating contacts: {e}")
        return
    output_path = os.path.join(output_path, "Chats")
    os.makedirs(output_path, exist_ok=True)
    width, height = A4  # Dimensions for the PDF page

    for contact_index, contact in enumerate(contacts, start=1):
        try:
            # Click on a contact to open the chat
            contact.click()
            time.sleep(5)

            # Locate the scrollable chat container
            ancestor_divs = driver.find_elements(By.CSS_SELECTOR, 'div.x78zum5.xdt5ytf.x1iyjqo2.xs83m0k.x1xzczws.x6ikm8r.x1odjw0f.x1n2onr6.xh8yej3.x16o0dkt')
            if len(ancestor_divs) < 2:
                print(f"Scrollable chat container not found for contact {contact_index}.")
                continue

            scrollable_div = ancestor_divs[1]

            # Scroll to the absolute top of the chat until no more scrolling is possible
            while True:
                # Save the current scroll position
                previous_scroll_position = driver.execute_script("return arguments[0].scrollTop;", scrollable_div)

                # Scroll further up
                driver.execute_script("arguments[0].scrollTop = 0;", scrollable_div)
                time.sleep(5)  # Allow content to load

                # Check if the scroll position changed
                new_scroll_position = driver.execute_script("return arguments[0].scrollTop;", scrollable_div)
                if new_scroll_position == previous_scroll_position:
                    break  # Top of the chat reached

            # Scroll through the chat and capture screenshots
            total_height = driver.execute_script("return arguments[0].scrollHeight;", scrollable_div)
            current_position = 0
            viewport_height = scrollable_div.size['height']
            screenshot_index = 1

            while current_position < total_height:
                screenshot_path = os.path.join(output_path, f"chat_{contact_index}_part{screenshot_index}.png")
                driver.save_screenshot(screenshot_path)

                # Add the screenshot to the PDF
                img = Image.open(screenshot_path)
                img_width, img_height = img.size
                aspect_ratio = img_height / img_width
                pdf_width = width - 60  # Margin of 30 on each side
                pdf_height = pdf_width * aspect_ratio
                x = (width - pdf_width) / 2
                y = (height - pdf_height) / 2
                pdf_report.drawImage(screenshot_path, x, y, width=pdf_width, height=pdf_height)
                pdf_report.showPage()

                # Scroll down the chat
                current_position += viewport_height
                driver.execute_script(f"arguments[0].scrollTop = {current_position};", scrollable_div)
                time.sleep(5)

                # Recalculate the total height for lazy loading
                total_height = driver.execute_script("return arguments[0].scrollHeight;", scrollable_div)
                screenshot_index += 1

            print(f"Captured chat for contact {contact_index}.")

        except Exception as e:
            print(f"Error capturing chat for contact {contact_index}: {e}")

    print("Completed fetching all chats.")
