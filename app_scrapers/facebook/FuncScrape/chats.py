import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from PIL import Image
from FuncScrape.pdf_utils import create_title_page, scale_image  # Import custom utilities
from reportlab.lib.pagesizes import A4

# Helper function to scroll and load all contacts
def scroll_to_load_contacts(driver, scrollable_div_selector):
    print("Loading all Facebook contacts...")
    try:
        scrollable_div = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, scrollable_div_selector))
        )
        last_height = driver.execute_script("return arguments[0].scrollHeight;", scrollable_div)
        while True:
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", scrollable_div)
            time.sleep(3)  # Allow time for content to load
            new_height = driver.execute_script("return arguments[0].scrollHeight;", scrollable_div)
            if new_height == last_height:
                break
            last_height = new_height
        print("All contacts loaded.")
    except TimeoutException:
        print("Unable to locate the scrollable contacts div.")

# Helper function to capture chat content and save as screenshots and PDF
def capture_chat(driver, pdf_report, output_path, chat_index, chat_div_selector):
    try:
        time.sleep(5)  # Allow the chat page to load

        # Locate the scrollable chat container
        chat_div = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, chat_div_selector)))[1]
        # Scroll to the top of the chat
        while True:
            prev_position = driver.execute_script("return arguments[0].scrollTop;", chat_div)
            driver.execute_script("arguments[0].scrollTop = 0;", chat_div)
            time.sleep(2)
            new_position = driver.execute_script("return arguments[0].scrollTop;", chat_div)
            if new_position == prev_position:
                break  # Reached the top

        # Capture screenshots while scrolling down
        total_height = driver.execute_script("return arguments[0].scrollHeight;", chat_div)
        current_position = 0
        viewport_height = chat_div.size['height']
        screenshot_index = 1

        while current_position < total_height:
            screenshot_path = os.path.join(output_path, f"chat_{chat_index}_part{screenshot_index}.png")
            driver.save_screenshot(screenshot_path)

            # Add screenshot to PDF using `scale_image`
            img = Image.open(screenshot_path)
            width, height = A4
            img_pdf_width, img_pdf_height = scale_image(img, width - 60, height - 60)  # 30 margin on all sides
            x = (width - img_pdf_width) / 2
            y = (height - img_pdf_height) / 2
            pdf_report.drawImage(screenshot_path, x, y, width=img_pdf_width, height=img_pdf_height)
            pdf_report.showPage()

            # Scroll down
            current_position += viewport_height
            driver.execute_script(f"arguments[0].scrollTop = {current_position};", chat_div)
            time.sleep(2)

            # Adjust for lazy-loading
            total_height = driver.execute_script("return arguments[0].scrollHeight;", chat_div)
            screenshot_index += 1

        print(f"Captured chat for contact {chat_index}.")
    except Exception as e:
        print(f"Error capturing chat for contact {chat_index}: {e}")

# Main function to fetch all chats
def fetch_chats(driver, pdf_report, output_path):
    time.sleep(15)
    driver.get("https://www.facebook.com/messages/")
    time.sleep(15)  # Allow the page to load

    # Create output directory for chat screenshots
    output_path = os.path.join(output_path, "Chats")
    os.makedirs(output_path, exist_ok=True)

    # Create title page for PDF
    create_title_page(pdf_report, "FACEBOOK CHATS")

    # Scroll and load all contacts
    scroll_to_load_contacts(driver, 'div.x78zum5.xdt5ytf.x1iyjqo2.x6ikm8r.x1odjw0f.x16o0dkt')
    
    contact_box=WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.x78zum5.xdt5ytf.x1iyjqo2.x6ikm8r.x1odjw0f.x16o0dkt'))  # Replace with actual selector
        )[0]
    try:
        # Locate all contacts
        contacts = contact_box.find_elements(By.CSS_SELECTOR, 'a')
        # Loop through contacts and capture chats
        for index, contact in enumerate(contacts, start=1):
            try:
                contact.click()
                time.sleep(5)  # Allow the chat to load

                # Capture chat content
                capture_chat(driver, pdf_report, output_path, index, 'div.x78zum5.xdt5ytf.x1iyjqo2.x6ikm8r.x1odjw0f.x16o0dkt')  
            except Exception as e:
                print(f"Error capturing chat for contact {index}: {e}")
    except TimeoutException:
        print("No contacts found.")
