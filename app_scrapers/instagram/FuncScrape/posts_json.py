import os
import time
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def fetch_posts_as_json(driver, username, f_upath):
    """Fetches image URLs from Instagram posts and saves them to a JSON file."""
    profile_url = f"https://www.instagram.com/{username}/"
    driver.get(profile_url)
    time.sleep(6)

    # Scroll down to load posts
    n_scrolls = 2
    for _ in range(n_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    time.sleep(4)

    # Extract post links
    post_links = []
    a_tags = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, 'a'))
    )

    for a in a_tags:
        href = a.get_attribute('href')
        if username+'/p/' in href and href not in post_links:
            post_links.append(href)

    print(f'Found {len(post_links)} posts.')

    # Initialize a list to hold the post data
    posts = []

    # Loop through each post link to extract image URLs
    for counter, post_link in enumerate(post_links, start=1):
        try:
            driver.get(post_link)
            time.sleep(3)

            # Initialize the post data with its link
            post_data = {
                "post_number": counter,
                "date": None,
                "time":None,
                "post_link": post_link,
                "images": [],
            }

            # Extract the date after opening the post
            try:
                date_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//time'))
                )
                post_data["date"] = date_element.get_attribute("datetime").split("T")[0]
                post_data["time"] = date_element.get_attribute("datetime").split("T")[1]
                print(f"Post {counter}: Date extracted.")
            except Exception as e:
                print(f"Post {counter}: Failed to extract date: {e}")

            # Extract the main image URL
            img_tag = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//img[@style="object-fit: cover;"]'))
            )
            img_url = img_tag.get_attribute('src')
            post_data["images"].append({
                "image_number": 1,
                "image_url": img_url
            })

            print(f"Post {counter}: Image 1 URL extracted.")

            # Handle multiple images (carousel posts)
            i = 2
            while True:
                try:
                    next_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Next"]')))
                    next_button.click()
                    time.sleep(2)

                    # Extract the next image URL
                    img_tag = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//img[@style="object-fit: cover;"]'))
                    )
                    img_url = img_tag.get_attribute('src')
                    post_data["images"].append({
                        "image_number": i,
                        "image_url": img_url
                    })

                    print(f"Post {counter}, Image {i}: Image URL extracted.")
                    i += 1

                except Exception:
                    print(f"No more images in post {counter}.")
                    break

            # Append the post data to the posts list
            posts.append(post_data)

        except Exception as e:
            print(f"Error processing post {counter}: {e}")
            continue

    # Save the extracted data to a JSON file
    path = os.path.join(f_upath,"Posts")
    os.makedirs(path, exist_ok=True)
    json_path = os.path.join(path, "posts.json")
    with open(json_path, "w") as json_file:
        json.dump(posts, json_file, indent=4)

    print(f"Post data saved to {json_path}.")
    return posts