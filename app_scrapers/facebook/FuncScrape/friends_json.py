import json
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def fetch_friends_as_json(driver, output_path):
    """
    Fetches the friends list from Facebook and saves it as a JSON file.

    Args:
        driver: Selenium WebDriver instance.
        output_path: Directory path to save the JSON file.
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

    # Extract all a tags containing friends' links
    try:
        a_tags = all_friends_container.find_elements(By.TAG_NAME, "a")
        if len(a_tags) <= 2:
            print("No friends found beyond the first two links. Exiting.")
            return

        # Skip the first two anchor tags
        a_tags = a_tags[2:]
        print(f"Number of friends found: {len(a_tags)}")

        # Prepare the JSON data
        friends_data = []

        for a_tag in a_tags:
            try:
                # Extract the profile link from the anchor tag
                profile_link = a_tag.get_attribute("href")

                # Extract the profile name from the span inside the anchor tag
                span = a_tag.find_element(
                    By.XPATH, ".//span[contains(@class, 'x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1f6kntn xvq8zen x1s688f xzsf02u')]"
                )
                profile_name = span.text

                if profile_name and profile_link:
                    friends_data.append({"profile_name": profile_name, "profile_link": profile_link})
                    print(f"Added: {profile_name} -> {profile_link}")

            except Exception as e:
                print(f"Error processing a tag or its span: {e}")
                continue

        # Save the JSON data to a file
        screenshots_path = os.path.join(output_path, "Friends")
        os.makedirs(screenshots_path, exist_ok=True)
        json_file_path = os.path.join(screenshots_path, "friends.json")
        with open(json_file_path, "w", encoding="utf-8") as json_file:
            json.dump(friends_data, json_file, ensure_ascii=False, indent=4)
        print(f"Friends data saved to {json_file_path}")
        return friends_data
    except Exception as e:
        print(f"Error processing friends list: {e}")
