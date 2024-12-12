import os
import time
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from fpdf import FPDF
from PIL import Image

driver = webdriver.Chrome()

output_dir = "chat_data"
os.makedirs(output_dir, exist_ok=True)

def login_and_extract_data():
    driver.get("https://web.whatsapp.com/")
    print("Waiting for QR code scan and page to load...")
    time.sleep(70)  

    # Extract all contact names with lazy scrolling
    contact_names = extract_contact_names()

    # Extract chats for each contact
    for contact_name in contact_names:
        try:
            print(f"Clicking on contact: {contact_name}")
            contact_element = driver.find_element(By.XPATH, f'//span[@title="{contact_name}"]')
            contact_element.click()
            time.sleep(5)  # Wait for the chat to load

            # Extract chat messages for the current contact
            chat_data = extract_chat_messages(contact_name)

            # Save the chat data in JSON format
            json_path = os.path.join(output_dir, f"{contact_name}_chat.json")
            with open(json_path, 'w', encoding='utf-8') as json_file:
                json.dump(chat_data, json_file, ensure_ascii=False, indent=4)

            print(f"Chat data saved for {contact_name} at: {json_path}")

            # Create a PDF of the chat for this contact
            create_pdf_of_chat(contact_name)
        except Exception as e:
            print(f"Error occurred while processing contact {contact_name}: {e}")

    driver.quit()

def extract_contact_names():
    contacts = []
    try:
        print("Scrolling through all contacts to load them completely...")
        scroll_count = 0
        contact_side = driver.find_element(By.CLASS_NAME, "x1n2onr6 _ak9y")

        while True:
            contact_elements = contact_side.find_elements(By.XPATH, "//span[@title]")
            for contact in contact_elements:
                contact_name = contact.get_attribute('title')
                if contact_name and contact_name not in contacts:
                    contacts.append(contact_name)
            
            driver.execute_script("arguments[0].scrollTop += 500;", contact_side)
            time.sleep(2)
            
            new_contact_elements = contact_side.find_elements(By.XPATH, "//span[@title]")
            if len(new_contact_elements) == len(contact_elements):
                scroll_count += 1
                if scroll_count >= 5:
                    print("Scrolled 5 extra times. Assuming all contacts are loaded.")
                    break
            else:
                scroll_count = 0

            contact_elements = new_contact_elements
        
    except Exception as e:
        print(f"Error while extracting contacts: {e}")
    return contacts

def extract_chat_messages(contact_name):
    messages = []
    try:
        chat_section = driver.find_element(By.CLASS_NAME, "x10l6tqk x13vifvy x17qophe xyw6214 x9f619 x78zum5 xdt5ytf xh8yej3 x5yr21d x6ikm8r x1rife3k xjbqb8w x1ewm37j")
        scroll_to_top(chat_section)

        message_elements = driver.find_elements(By.XPATH, '//div[contains(@class, "copyable-text")]')

        for message_element in message_elements:
            try:
                date_time = message_element.get_attribute("data-pre-plain-text")
                name_match = re.match(r'^\[(.*?)] (.*?): ', date_time)
                sender_name = name_match.group(2) if name_match else "Unknown"

                whoc = message_element.find_elements(By.XPATH, './/span[contains(@class, "selectable-text") and contains(@class, "copyable-text")]')
                if whoc:
                    message_content = whoc[0].text.strip()
                    if date_time and message_content:
                        message_data = {
                            "dateTime": date_time,
                            "message": message_content,
                            "sender": sender_name
                        }
                        messages.append(message_data)
            except Exception as e:
                print(f"Error extracting message: {e}")
    except Exception as e:
        print(f"Error occurred while extracting chat for {contact_name}: {e}")
    return messages

def scroll_to_top(element):
    print("Scrolling to the top to load all messages...")
    current_scroll = driver.execute_script("return arguments[0].scrollTop;", element)
    while current_scroll > 0:
        previous_scroll = current_scroll
        driver.execute_script("arguments[0].scrollTop -= 500;", element)
        time.sleep(10)  # Wait for lazy loading
        current_scroll = driver.execute_script("return arguments[0].scrollTop;", element)
        if current_scroll == previous_scroll:
            print("Reached the top of the chat, all messages loaded.")
            break
    print("Scrolling to the top complete.")

def create_pdf_of_chat(contact_name):
    print(f"Capturing chat for {contact_name} as screenshots, cropping them, and bundling into a PDF...")
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    screenshot_counter = 0

    chat_section = driver.find_element(By.CLASS_NAME, "x10l6tqk x13vifvy x17qophe xyw6214 x9f619 x78zum5 xdt5ytf xh8yej3 x5yr21d x6ikm8r x1rife3k xjbqb8w x1ewm37j")

    while True:
        screenshot_path = os.path.join(output_dir, f"{contact_name}_screenshot_{screenshot_counter}.png")
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot {screenshot_counter} taken for {contact_name}.")

        cropped_path = os.path.join(output_dir, f"{contact_name}_cropped_{screenshot_counter}.png")
        with Image.open(screenshot_path) as img:
            width, height = img.size
            right_half = img.crop((width // 2, 0, width, height))
            right_half.save(cropped_path)

        pdf.add_page()
        pdf.image(cropped_path, x=10, y=10, w=190)

        previous_scroll = driver.execute_script("return arguments[0].scrollTop;", chat_section)
        driver.execute_script("arguments[0].scrollTop -= 500;", chat_section)
        time.sleep(10)  # Wait for lazy loading
        current_scroll = driver.execute_script("return arguments[0].scrollTop;", chat_section)

        if current_scroll == previous_scroll:
            print(f"Reached the top of the chat for {contact_name}.")
            break

        screenshot_counter += 1

    pdf_output_path = os.path.join(output_dir, f"{contact_name}_chat.pdf")
    pdf.output(pdf_output_path)
    print(f"PDF saved to {pdf_output_path}")


login_and_extract_data()
