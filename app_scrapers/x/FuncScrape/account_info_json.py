import os
import json
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def fetch_account_details_as_json(driver, f_upath):
    # Path for JSON output
    path = os.path.join(f_upath, "Account_Details")
    os.makedirs(path, exist_ok=True)
    json_path = os.path.join(path, "account_details.json")

    account_details = {}

    try:
        # Navigate to the specified Twitter/X account data page
        driver.get("https://x.com/settings/your_twitter_data/account")
        print("Navigating to Twitter/X account data settings...")
        time.sleep(5)

        # Locate details in the "Section details" aria-label section
        section_details = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'section[aria-label="Section details"]'))
        )

        # Helper function to extract key-value pairs
        def extract_details(a_tag_selector, key_name):
            try:
                a_tag = section_details.find_element(By.CSS_SELECTOR, a_tag_selector)
                spans = a_tag.find_elements(By.CSS_SELECTOR, 'span.css-1jxf684.r-bcqeeo.r-1ttztb7.r-qvutc0.r-poiln3')
                key = spans[0].text if len(spans) >= 1 else None
                value = spans[1].text if len(spans) > 1 else None
                account_details[key_name] = {"key": key, "value": value}
            except Exception as e:
                print(f"Unable to extract details for {key_name}: {e}")

        # Fetch key-value pairs from the required sections
        extract_details('a[href="/settings/screen_name"]', "Screen Name")
        extract_details('a[href="/settings/phone"]', "Phone Number")
        extract_details('a[href="/settings/email"]', "Email Address")
        extract_details('a[href="/settings/country"]', "Country")
        extract_details('a[href="/settings/languages"]', "Languages")
        extract_details('a[href="/settings/your_twitter_data/gender"]', "Gender")
        extract_details('a[href="/settings/your_twitter_data/age"]', "Age")

        # Special case for account creation date, time, and IP
        try:
            creation_div = section_details.find_element(By.CSS_SELECTOR, 'div[data-testid="account-creation"]')
            spans = creation_div.find_elements(By.CSS_SELECTOR, 'span.css-1jxf684.r-bcqeeo.r-1ttztb7.r-qvutc0.r-poiln3')

            creation_date_time = spans[1].text if len(spans) > 1 else None
            ip_info = spans[2].text if len(spans) > 2 else None

            if creation_date_time:
                account_details["Account Creation"] = {
                    "Date and Time": creation_date_time,
                    "IP Address": ip_info.split(" (")[0] if ip_info and "(" in ip_info else None
                }
        except Exception as e:
            print(f"Error extracting account creation details: {e}")


        # Save the account details to a JSON file
        with open(json_path, "w", encoding="utf-8") as file:
            json.dump(account_details, file, indent=4)
            print(f"Account details saved to {json_path}")
        return account_details
    except TimeoutException as e:
        print(f"Error: {e}")
        return {}
