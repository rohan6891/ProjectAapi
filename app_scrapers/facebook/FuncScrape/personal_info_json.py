import os
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def fetch_personal_info_as_json(driver, output_path):
    """
    Extracts personal information from the "About Contact and Basic Info" section of a Facebook profile 
    using the `c_user` cookie.

    Args:
        driver: Selenium WebDriver instance.
        output_path: Directory path to save the JSON file.
    """

    # Get `c_user` value from cookies
    try:
        c_user = driver.get_cookie("c_user")["value"]
        print(f"c_user: {c_user}")
    except Exception as e:
        print(f"Error fetching c_user cookie: {e}")
        return

    # Navigate to the "About Contact and Basic Info" section
    profile_url = f"https://www.facebook.com/profile.php?id={c_user}&sk=about_contact_and_basic_info"
    driver.get(profile_url)
    print(f"Navigated to URL: {profile_url}")

    # Wait for the contact info section to load
    try:
        contact_info_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class, 'xyamay9 xqmdsaz x1gan7if x1swvt13')]")
            )
        )
        print("Contact information section loaded.")
    except Exception as e:
        print(f"Error locating contact information section: {e}")
        return

    # Extract keys and values
    try:
        # Extract all keys
        key_elements = contact_info_div.find_elements(
            By.XPATH,
            ".//span[contains(@class, 'x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1pg5gke xvq8zen xo1l8bm xi81zsa x1yc453h')]//div"
        )
        keys = [key.text.strip() for key in key_elements if key.text.strip()]

        # Extract all values
        value_elements = contact_info_div.find_elements(
            By.XPATH,
            ".//span[contains(@class, 'x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x3x7a5m x1f6kntn xvq8zen xo1l8bm xzsf02u x1yc453h')]"
        )
        values = [value.text.strip() for value in value_elements if value.text.strip()]

        # Map keys to values
        personal_info = dict(zip(keys, values))
        print(f"Extracted Personal Information: {personal_info}")
    except Exception as e:
        print(f"Error extracting keys or values: {e}")
        return

    # Save to JSON
    try:
        output_path = os.path.join(output_path, "Personal_info")
        os.makedirs( output_path, exist_ok=True)
        json_path = os.path.join(output_path, "personal_info.json")
        with open(json_path, "w") as json_file:
            json.dump(personal_info, json_file, indent=4)
        print(f"Personal information saved to {json_path}")
        return personal_info
    except Exception as e:
        print(f"Error saving personal information to JSON: {e}")
        return

    print("Finished extracting personal information.")
