import os
import time
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def fetch_followers_as_json(driver, username, output_path):
    """
    Fetches followers from Instagram and saves them as a JSON file.
    Args:
        driver: Selenium WebDriver instance.
        username: Instagram username whose followers to fetch.
        output_path: Directory path to save the JSON file.
    """
    profile_url = f"https://www.instagram.com/{username}/"
    driver.get(profile_url)
    time.sleep(6)

    # Locate and click the followers link
    try:
        followers_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//a[@href='/{username}/followers/']"))
        )
        followers_link.click()
        print("Navigated to followers page.")
    except Exception as e:
        print(f"Error locating followers link: {e}")
        return

    # Wait for the followers modal to load
    time.sleep(3)

    # Define the scrolling container XPath
    scrolling_div_xpath = "//div[contains(@class, 'xyi19xy x1ccrb07 xtf3nb5 x1pc53ja x1lliihq x1iyjqo2 xs83m0k xz65tgg x1rife3k x1n2onr6')]"

    try:
        scrolling_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, scrolling_div_xpath))
        )
    except Exception as e:
        print(f"Error locating scrolling container: {e}")
        return

    # Scroll until the bottom
    previous_scroll_position = 0
    while True:
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", scrolling_div)
        time.sleep(6)  # Wait for content to load
        current_scroll_position = driver.execute_script("return arguments[0].scrollTop;", scrolling_div)
        if current_scroll_position == previous_scroll_position:
            print("Reached the bottom of the followers list.")
            break
        previous_scroll_position = current_scroll_position

    # Fetch all the relevant divs
    try:
        divs_with_auto_style = driver.find_elements(By.XPATH, "//div[@style='height: auto; overflow: hidden auto;']")
        if len(divs_with_auto_style) < 1:
            print("No follower container found.")
            return
        followers_div = divs_with_auto_style[0]  # Take the first one
    except Exception as e:
        print(f"Error locating followers div: {e}")
        return

    # Extract profile details (IDs and links)
    followers_data = []
    try:
        spans = followers_div.find_elements(By.XPATH, ".//span[contains(@class, '_ap3a _aaco _aacw _aacx _aad7 _aade')]")
        for span in spans:
            try:
                profile_id = span.text
                profile_link_element = span.find_element(By.XPATH, "./ancestor::a[@href]")
                profile_link = profile_link_element.get_attribute("href")
                followers_data.append({"profile_id": profile_id, "profile_link": profile_link})
            except Exception as e:
                print(f"Error extracting profile details for a span: {e}")
    except Exception as e:
        print(f"Error locating span elements: {e}")
        return

    # Save to JSON file
    output_path = os.path.join(output_path, "Followers")
    os.makedirs(output_path, exist_ok=True)
    json_file_path = os.path.join(output_path, "followers.json")
    with open(json_file_path, "w", encoding="utf-8") as json_file:
        json.dump(followers_data, json_file, indent=4, ensure_ascii=False)
    print(f"Saved ${len(followers_data)} followers  data to {json_file_path}.")
    return followers_data
