from selenium.webdriver.common.by import By
from PIL import Image
import time

from reportlab.lib.pagesizes import A4
from FuncScrape.pdf_utils import create_title_page
from FuncScrape.pdf_utils import scale_image
import os
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException


def scroll_to_load_contacts(driver, contacts_locator):
    print("Loading all contacts...")
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Allow content to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    print("All contacts loaded.")



def fetch_chats(driver, pdf_report,f_upath):
    driver.get("https://x.com/messages")
    time.sleep(10)
    path = os.path.join(f_upath,"Chats")
    os.makedirs(path, exist_ok=True)
    create_title_page(pdf_report, "CHATS")
    # Add title page for chats
    width, height = A4
    try:
        # Scroll to load all contacts using the `scroll_to_load_contacts` function
        scroll_to_load_contacts(driver, 'div[role="listitem"]')
        # Locate contacts by class name
        contacts = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[data-testid="conversation"]'))
        )

        for index, contact in enumerate(contacts, start=1):
            contact.click()
            time.sleep(10)

            # Locate the chat section by class name
            chat_section = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="DmActivityViewport"]'))
            )

            print(f"Capturing chat for contact {index}...")
            
            # Scroll to the top of the chat
            driver.execute_script("arguments[0].scrollTop = 0;", chat_section)
            time.sleep(5)

            # Get the total height of the chat section
            total_height = driver.execute_script("return arguments[0].scrollHeight;", chat_section)
            current_position = 0
            scroll_offset = chat_section.size['height']  # Use the visible height of the chat section

            print("Starting chat capture...")
            while current_position < total_height:
                # Save screenshot of the visible part of the chat
                screenshot_path =os.path.join(path, f"chat_{index}_pos_{current_position}.png") 
                driver.save_screenshot(screenshot_path)

                # Insert the screenshot into the PDF
                img = Image.open(screenshot_path)
                img_pdf_width, img_pdf_height = scale_image(img, width - 2 * 30, height - 2 * 30)
                x = (width - img_pdf_width) / 2
                y = (height - img_pdf_height) / 2
                pdf_report.drawImage(screenshot_path, x, y, width=img_pdf_width, height=img_pdf_height)
                pdf_report.showPage()

                # Scroll down by the window's visible height
                current_position += scroll_offset
                driver.execute_script(f"arguments[0].scrollTop = {current_position};", chat_section)
                time.sleep(2)

                # Recalculate total height (in case it changes due to lazy loading)
                total_height = driver.execute_script("return arguments[0].scrollHeight;", chat_section)

            print(f"Finished capturing chat for contact {index}.")

    except TimeoutException:
        print("Failed to load chat contacts or chats.")
