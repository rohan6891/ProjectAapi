import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import os

def fetch_chats_json(driver,f_upath):
    driver.get("https://x.com/messages")
    time.sleep(10)
    path = os.path.join(f_upath,"Chats")
    os.makedirs(path, exist_ok=True)

    all_chats = []  # List to store all contact chats
    visited_profile_links = set()  # Set to track already added profile links

    try:
        # Load all contacts
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

        # Locate all contact elements
        contacts = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[data-testid="conversation"]'))
        )

        for contact in contacts:
            # Click on the contact to open chat
            contact.click()
            time.sleep(5)

            # Retrieve the Receiver's name
            try:
                name_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "detail-header"))
                )
                receiver_name = name_element.find_element(By.TAG_NAME, "span").text
            except TimeoutException:
                print("Receiver name not found, skipping contact...")
                continue

            # Retrieve the Profile link (exclude unwanted link)
            try:
                # Select all <a> tags in the div with data-testid="cellInnerDiv"
                profile_links = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="cellInnerDiv"] a[role="link"]')
                profile_link = None
                for link in profile_links:
                    href = link.get_attribute('href')
                    if href != "https://x.com/i/keyboard_shortcuts" and href not in visited_profile_links:
                        profile_link = href
                        visited_profile_links.add(href)  # Mark this profile link as visited
                        break

                if not profile_link:
                    print(f"No valid profile link found for {receiver_name}, skipping contact.")
                    continue
            except Exception as e:
                print(f"Profile link not found for {receiver_name}, skipping contact. Error: {e}")
                continue

            # Locate chat section
            try:
                chat_section = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="DmActivityViewport"]'))
                )
            except TimeoutException:
                print(f"Chat section not found for {receiver_name}. Skipping...")
                continue

            # Scroll to the top to load all messages
            print(f"Scrolling to the top for {receiver_name}...")
            while True:
                previous_scroll_height = driver.execute_script("return arguments[0].scrollTop;", chat_section)
                driver.execute_script("arguments[0].scrollTop = 0;", chat_section)
                time.sleep(2)  # Wait for loading
                current_scroll_height = driver.execute_script("return arguments[0].scrollTop;", chat_section)
                if previous_scroll_height == current_scroll_height:
                    break
            print(f"All messages loaded for {receiver_name}.")

            # Capture all messages after scrolling to the top
            contact_chat = {"receiver_name": receiver_name, "profile_link": profile_link, "chat": []}

            messages = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="tweetText"] span')
            for message in messages:
                parent_div = message.find_element(By.XPATH, "./ancestor::div[@role='presentation']")
                if 'r-l5o3uw' in parent_div.get_attribute('class'):
                    sender = "Sender"
                elif 'r-gu4em3' in parent_div.get_attribute('class'):
                    sender = "Receiver"
                else:
                    sender = "Unknown"
                message_text = message.text.strip()

                # Add message directly to the chat
                contact_chat["chat"].append({"sender": sender, "message": message_text})

            # Append contact chat to all chats
            all_chats.append(contact_chat)
            print(f"Finished fetching chat for {receiver_name}.")

            # Return to contact list
            driver.back()
            time.sleep(5)

    except TimeoutException:
        print("Failed to load chat contacts or chats.")

    # Save all chats to JSON file
    output_file = os.path.join(path, "chats.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_chats, f, indent=4)
    print(f"All chats saved to {output_file}.")
    return all_chats