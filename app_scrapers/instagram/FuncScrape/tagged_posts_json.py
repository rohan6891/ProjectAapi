from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import json

def fetch_tagged_posts_as_json(driver, username, f_upath):
    """Fetches tagged posts of a user and saves the data as JSON."""
    tagged_posts_url = f"https://www.instagram.com/{username}/tagged/"
    driver.get(tagged_posts_url)
    time.sleep(6)

    # Scroll the page to load more posts
    n_scrolls = 2
    for _ in range(n_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    time.sleep(4)

    # Find and collect post links
    post_links = []
    a_tags = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, 'a'))
    )

    # Loop through all anchor tags and collect links to Instagram posts
    for a in a_tags:
        href = a.get_attribute('href')
        if '/p/' in href and href not in post_links:
            post_links.append(href)

    print(f'Found {len(post_links)} tagged posts.')

    # Prepare JSON structure
    tagged_posts_data = []

    # Iterate over each post link and collect data
    for counter, post_link in enumerate(post_links, start=1):
        try:
            driver.get(post_link)
            time.sleep(3)

            # Initialize data for this post
            post_data = {
                "post_number": counter,
                "post_link": post_link,
                "images": []
            }

            # Extract the main image URL
            try:
                img_tag = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//img[@style="object-fit: cover;"]'))
                )
                img_url = img_tag.get_attribute('src')
                post_data["images"].append({
                    "image_number": 1,
                    "image_url": img_url,
                    "image_summary":""
                })
                print(f"Tagged Post {counter}: Image 1 URL extracted.")
            except Exception as img_error:
                print(f"Error extracting main image for tagged post {counter}: {img_error}")

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
                        "image_url": img_url,
                        "image_summary":""
                    })

                    print(f"Tagged Post {counter}, Image {i}: Image URL extracted.")
                    i += 1

                except Exception:
                    print(f"No more images in tagged post {counter}.")
                    break

            # Append this post's data to the JSON list
            tagged_posts_data.append(post_data)

        except Exception as e:
            print(f"Error processing tagged post {counter}: {e}")
            continue

    # Save the JSON data to a file
    path = os.path.join(f_upath, "Tagged_Posts")
    os.makedirs(path, exist_ok=True)
    json_path = os.path.join(path, "tagged_posts.json")
    with open(json_path, "w") as json_file:
        json.dump(tagged_posts_data, json_file, indent=4)

    print(f"Tagged posts data saved to {json_path}.")
    return tagged_posts_data
