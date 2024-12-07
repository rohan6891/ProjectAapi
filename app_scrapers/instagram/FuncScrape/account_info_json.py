import os
import time
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def fetch_account_info_as_json(driver, username, output_path):
    """
    Fetches account information from Instagram and saves it as a JSON file.
    Args:
        driver: Selenium WebDriver instance.
        username: Instagram username for navigating to the profile.
        output_path: Directory path to save the JSON file.
    """
    profile_url = f"https://www.instagram.com/{username}/"
    driver.get(profile_url)
    time.sleep(6)

    # Navigate to the accounts center URL
    accounts_center_url = "https://accountscenter.instagram.com/personal_info/"
    driver.get(accounts_center_url)
    time.sleep(6)

    account_info = {"username": username}

    # Fetch Contact Points
    try:
        contact_points_anchor = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/contact_points/')]"))
        )
        contact_points_anchor.click()
        time.sleep(4)

        contact_divs = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'x16n37ib xq8finb')]"))
        )

        contact_info = []
        for div in contact_divs:
            try:
                first_child = div.find_element(By.XPATH, ".//div[1]")
                contact_text = first_child.text.strip()
                if "@" in contact_text:
                    contact_info.append({"type": "email", "value": contact_text})
                elif contact_text.isdigit():
                    contact_info.append({"type": "phone", "value": contact_text})
                else:
                    contact_info.append({"type": "other", "value": contact_text})
            except Exception as e:
                print(f"Error extracting contact info: {e}")

        # Only add contact info if available
        if contact_info:
            account_info["contacts"] = contact_info
    except Exception as e:
        print(f"Error fetching contact points: {e}")

    # Navigate back to accounts center URL
    driver.get(accounts_center_url)
    time.sleep(4)

    # Fetch Birthday
    try:
        birthday_anchor = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/personal_info/birthday/?entrypoint=accounts_center')]"))
        )
        birthday_anchor.click()
        time.sleep(4)

        birthday_divs = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'xq8finb')]"))
        )
        if birthday_divs:
            birthday_div = birthday_divs[-1]  # Get the last div in the list
            birthday_text = birthday_div.find_element(By.XPATH, ".//div").text.strip()
            if birthday_text:
                account_info["birthday"] = birthday_text
    except Exception as e:
        print(f"Error fetching birthday: {e}")

    # Save to JSON file
    output_path= os.path.join(output_path, "AccountInfo")
    os.makedirs(output_path, exist_ok=True)
    json_file_path = os.path.join(output_path, "account_info.json")
    with open(json_file_path, "w", encoding="utf-8") as json_file:
        json.dump(account_info, json_file, indent=4, ensure_ascii=False)

    print(f"Account information for {username} saved to {json_file_path}.")
    return account_info
