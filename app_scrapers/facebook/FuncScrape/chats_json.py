import json
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from collections import OrderedDict

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


def scroll_to_top(driver, chat_div):
    print("Scrolling to the top of the chat...")
    while True:
        prev_height = driver.execute_script("return arguments[0].scrollHeight;", chat_div)
        driver.execute_script("arguments[0].scrollTop = 0;", chat_div)  # Scroll to the top
        time.sleep(2)  # Allow content to load

        # Check if the height remains the same (no new content is loaded)
        new_height = driver.execute_script("return arguments[0].scrollHeight;", chat_div)
        if new_height == prev_height:
            break  # Fully scrolled to the top
    print("Reached the top of the chat.")

def capture_chat(driver, chat_div_selector):
    try:
        time.sleep(5)  # Allow the chat page to load

        # Locate the scrollable chat container
        chat_div = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, chat_div_selector)))[1]

        # Scroll to the top of the chat
        scroll_to_top(driver, chat_div)

        # Get receiver's name and profile link
        receiver_name_element = chat_div.find_element(By.CSS_SELECTOR, 'span')  # Update selector if necessary
        receiver_name = receiver_name_element.text.strip() if receiver_name_element else "Unknown"
        
        # Find the receiver's profile link
        receiver_profile_link_element = driver.find_element(By.CSS_SELECTOR, 'a[aria-label="' + receiver_name + '"]')
        receiver_profile_link = receiver_profile_link_element.get_attribute("href") if receiver_profile_link_element else "No link found"

        # Track unique div elements while preserving the order
        all_message_divs = OrderedDict()  # Using OrderedDict to maintain order and uniqueness
        messages = []  # List to store the messages

        total_height = driver.execute_script("return arguments[0].scrollHeight;", chat_div)
        current_position = 0
        viewport_height = chat_div.size['height']

        while current_position < total_height:
            message_divs = chat_div.find_elements(By.CSS_SELECTOR, 
                                                  'div.html-div.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x1gslohp.x11i5rnm.x12nagc.x1mh8g0r.x1yc453h.x126k92a')
            for message_div in message_divs:
                # Use div reference as the key to track uniqueness
                if message_div not in all_message_divs:
                    all_message_divs[message_div] = True  # Add unique div to OrderedDict

                    # Extract message text immediately
                    message_text = message_div.text.strip()
                    if not message_text:
                        continue  # Skip empty messages

                    # Determine sender
                    if "x18lvrbx" in message_div.get_attribute("class"):
                        sender = "Receiver"
                    else:
                        sender = "Sender"

                    # Append the message to the list immediately after inserting into OrderedDict
                    messages.append({"sender": sender, "message": message_text})

            # Scroll down
            current_position += viewport_height
            driver.execute_script(f"arguments[0].scrollTop = {current_position};", chat_div)
            time.sleep(2)

            # Adjust for lazy-loading
            total_height = driver.execute_script("return arguments[0].scrollHeight;", chat_div)

        return {
            "receiver_name": receiver_name,
            "receiver_profile_link": receiver_profile_link,
            "chat": messages
        }

    except Exception as e:
        print(f"Error capturing chat for contact: {e}")
        return None

# Main function to fetch all chats
def fetch_chats_as_json(driver, output_path):
    time.sleep(15)
    driver.get("https://www.facebook.com/messages/")
    time.sleep(15)  # Allow the page to load

    # Create output directory for chat screenshots
    output_path = os.path.join(output_path, "Chats")
    chats_data=[]
    os.makedirs(output_path, exist_ok=True)
    # Scroll and load all contacts
    scroll_to_load_contacts(driver, 'div.x78zum5.xdt5ytf.x1iyjqo2.x6ikm8r.x1odjw0f.x16o0dkt')
    
    contact_box=WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.x78zum5.xdt5ytf.x1iyjqo2.x6ikm8r.x1odjw0f.x16o0dkt'))
        )[0]
    try:
        # Locate all contacts
        contact_links = [
            contact.get_attribute('href')
            for contact in contact_box.find_elements(By.CSS_SELECTOR, 'a')
        ]
        # Loop through contacts and capture chats
        for index, link in enumerate(contact_links, start=1):
            try:
                driver.get(link)
                time.sleep(5)  # Allow the chat to load

                # Capture chat content
                data=capture_chat(driver, 'div.x78zum5.xdt5ytf.x1iyjqo2.x6ikm8r.x1odjw0f.x16o0dkt')  
                chats_data.append(data)          
            except Exception as e:
                print(f"Error capturing chat for contact {index}: {e}")
        output_file = os.path.join(output_path, "chats.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(chats_data, f, ensure_ascii=False, indent=4)
        print(f"Chats saved to {output_file}")
        return chats_data          
    except TimeoutException:
        print("No contacts found.")





