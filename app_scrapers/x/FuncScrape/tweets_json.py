from selenium.webdriver.common.by import By
import time
import json
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
def fetch_tweets_json(driver, username, f_upath):
    profile_url = f"https://x.com/{username}"
    driver.get(profile_url)
    time.sleep(5)

    # Create directory to store tweets JSON file
    path = os.path.join(f_upath, "Tweets")
    os.makedirs(path, exist_ok=True)

    tweet_links = []
    n_scrolls = 2  # Adjust the number of scrolls if needed

    # Step 1: Collect all tweet links by scrolling
    for _ in range(n_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        tweets = driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')
        for tweet in tweets:
            try:
                link = tweet.find_element(By.CSS_SELECTOR, 'a[href*="/status/"]').get_attribute('href')
                if link and link not in tweet_links:
                    tweet_links.append(link)
            except:
                continue

    tweet_data = []

    # Step 2: Visit each tweet link and extract details
    for tweet_link in tweet_links:
        driver.get(tweet_link)
        time.sleep(5)

        try:
            # Find the article with tweet content
            tweet_element = driver.find_element(By.CSS_SELECTOR, 'article[data-testid="tweet"]')

            # Extract tweet text
            tweet_text = None
            try:
                tweet_text_elem = tweet_element.find_element(By.CSS_SELECTOR, 'div[data-testid="tweetText"] span')
                tweet_text = tweet_text_elem.text.strip()
            except:
                pass
            # Extract date and time
            try:
                date_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//time'))
                )
                date_str = date_element.get_attribute("datetime").split("T")[0]
                time_str = date_element.get_attribute("datetime").split("T")[1]
            except Exception as e:
                print(f"Failed to extract date: {e}")
            # Extract image link
            img_link = None
            try:
                img_elem = tweet_element.find_element(By.CSS_SELECTOR, 'div[data-testid="tweetPhoto"][aria-label="Image"] img')
                img_link = img_elem.get_attribute("src")
            except:
                pass

            # Append the extracted data based on available content
            tweet_entry = {
                "date": date_str.strip(),
                "time": time_str.strip(),
            }
            if tweet_text:
                tweet_entry["tweet"] = tweet_text
            if img_link:
                tweet_entry["image_link"] = img_link
                tweet_entry["image_summary"]=""

            tweet_data.append(tweet_entry)

        except Exception as e:
            print(f"Error processing tweet at {tweet_link}: {e}")
            continue

    # Step 3: Save the data to a JSON file
    json_file_path = os.path.join(path, "tweets.json")
    with open(json_file_path, "w", encoding="utf-8") as json_file:
        json.dump(tweet_data, json_file, ensure_ascii=False, indent=4)
    return tweet_data
