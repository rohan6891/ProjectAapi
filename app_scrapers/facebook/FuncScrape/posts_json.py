import os
import time
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def fetch_posts_as_json(driver, username, output_path):
    """
    Fetches posts from Facebook for a given user and adds screenshots of the 4th anchor tag in each post div to a PDF.
    
    Args:
        driver: Selenium WebDriver instance.
        pdf_report: ReportLab PDF canvas object for adding pages.
        username: Facebook username to locate the profile.
        output_path: Directory path to save screenshots and PDF.
    """

    base_url = "https://www.facebook.com/"
    driver.get(base_url)
    time.sleep(5)

    # Locate and click the profile link
    try:
        user_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//a[.//span[text()='{username}']]")
            )
        )
        user_link.click()
        print(f"Navigated to {username}'s profile.")
    except Exception as e:
        print(f"Error locating profile link: {e}")
        return
    # Locate and click the profile link
    time.sleep(5)

    # Scroll to the bottom of the profile and back to the top
    try:
        for _ in range(5):  # Arbitrary scroll count; adjust if needed
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")
        print("Scrolled through the profile.")
    except Exception as e:
        print(f"Error during scrolling: {e}")
        return

    # Locate the main container for posts
    try:
        posts_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class, 'x9f619 x1n2onr6 x1ja2u2z xeuugli xs83m0k xjl7jj x1xmf6yo x1emribx x1e56ztr x1i64zmx x19h7ccj xu9j1y6 x7ep2pv')]")
            )
        )
    except Exception as e:
        print(f"Error locating posts container: {e}")
        return

    # Create directory for saving screenshots
    output_path = os.path.join(output_path, "Posts")
    os.makedirs(output_path, exist_ok=True)
    # Create directory for saving JSON
    json_path = os.path.join(output_path, "posts.json")
    post_data = []

    # Iterate through post divs
    try:
        post_divs = posts_container.find_elements(
            By.XPATH,
            ".//div[contains(@class, 'x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z')]"
        )
        if not post_divs:
            print("No more posts found.")
        print("Number of Posts: ", len(post_divs))
        post_index = 1
        for post_div in post_divs:
            # Locate the 4th anchor tag within the post div
            a_tags = post_div.find_elements(By.TAG_NAME, "a")
            if len(a_tags) >= 4:  # Check if the 4th anchor tag exists
                try:
                    a_tags[3].click()  # Click the 4th anchor tag
                    time.sleep(3)

                    # Take screenshot
                    post_link = driver.current_url
                    post_data.append({"post_number": post_index, "post_link": post_link})
                    print(f"Captured link for post {post_index}: {post_link}")

                    # Return to the post container
                    driver.back()
                    time.sleep(2)
                    post_index += 1
                except Exception as e:
                    print(f"Error processing 4th anchor tag in post: {e}")
                    continue
            else:
                print(f"Post div does not have 4 anchor tags. Skipping this div.")

            # Scroll down a bit to load more posts
            driver.execute_script("arguments[0].scrollBy(0, 500);", posts_container)
            time.sleep(2)
        # Save the post data to a JSON file
        with open(json_path, "w") as json_file:
            json.dump(post_data, json_file, indent=4)

        print(f"Post links saved to {json_path}")
        return post_data
    except Exception as e:
        print(f"Error processing posts: {e}")
            

    print("Finished capturing Facebook posts.")