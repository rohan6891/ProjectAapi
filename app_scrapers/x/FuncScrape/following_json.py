from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import os


def fetch_following_json(driver, username, f_upath):
    # Navigate to the "Following" page
    following_url = f"https://x.com/{username}/following"
    driver.get(following_url)
    time.sleep(5)

    # Create a directory to store the JSON file
    path = os.path.join(f_upath, "Following")
    os.makedirs(path, exist_ok=True)

    # Locate the "Following" timeline section
    timeline_section = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div[aria-label="Timeline: Following"]'))
    )

    profile_links = set()  # To store unique profile links

    current_position = 0
    scroll_offset = driver.execute_script("return window.innerHeight;")  # Scroll by the visible window height
    total_height = driver.execute_script("return arguments[0].scrollHeight;", timeline_section)

    print("Extracting profile links from the 'Following' page...")

    while current_position < total_height:
        # Find all follower divs
        follower_divs = timeline_section.find_elements(By.CSS_SELECTOR, 'div[data-testid="cellInnerDiv"]')

        for follower_div in follower_divs:
            try:
                # Extract profile link
                profile_link_elem = follower_div.find_element(By.CSS_SELECTOR, 'a')
                profile_link = profile_link_elem.get_attribute("href")
                profile_links.add(profile_link)
            except Exception as e:
                print(f"Error extracting profile link: {e}")
                continue

        # Scroll down by the offset
        current_position += scroll_offset
        driver.execute_script(f"window.scrollTo(0, {current_position});")
        time.sleep(2)  # Allow content to load

        # Recalculate the total height (in case it changes due to lazy loading)
        total_height = driver.execute_script("return arguments[0].scrollHeight;", timeline_section)

    print(f"Total profile links extracted: {len(profile_links)}")

    # Extract names from profile links
    following_data = []

    for profile_link in profile_links:
        try:
            # Navigate to the profile page
            driver.get(profile_link)
            time.sleep(5)

            # Extract the name from the profile page
            name = None
            try:
                user_name_div = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="UserName"]')
                name_span = user_name_div.find_element(By.XPATH, './/span[normalize-space(text())]')
                name = name_span.text.strip()
            except Exception as e:
                print(f"Failed to extract name for {profile_link}: {e}")

            # Append data to the JSON list
            if name:
                following_data.append({"name": name, "profile_link": profile_link})
        except Exception as e:
            print(f"Error processing profile {profile_link}: {e}")
            continue

        # Navigate back to the "Following" page
        driver.get(following_url)
        time.sleep(5)

    # Save the data to a JSON file
    json_file_path = os.path.join(path, "following.json")
    with open(json_file_path, "w", encoding="utf-8") as json_file:
        json.dump(following_data, json_file, ensure_ascii=False, indent=4)
    return following_data