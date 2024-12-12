import os
import time
import json
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By

def fetch_comments_as_json(driver, f_upath):
    """Fetches Instagram comments and saves them in JSON format."""
    driver.get("https://www.instagram.com/your_activity/interactions/comments")
    time.sleep(6)

    path = os.path.join(f_upath, "Comments")
    os.makedirs(path, exist_ok=True)

    scrollable_div = driver.find_element(By.XPATH, '//div[@data-bloks-name="bk.components.Collection"]')

    # Scroll to the bottom
    while True:
        prev_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
        time.sleep(2)
        curr_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
        if curr_height == prev_height:
            break

    # Scroll back to the top
    driver.execute_script("arguments[0].scrollTop = 0", scrollable_div)
    time.sleep(2)

    comments_data = []

    while True:
        try:
            # Re-fetch comments container and spans
            comments_container = driver.find_element(By.XPATH, '//div[@data-testid="comments_container_non_empty_state"]')

            spans = comments_container.find_elements(By.XPATH, './/span[@data-bloks-name="bk.components.TextSpan"]')
            filtered_comments = [
                spans[i].text
                for i in range(len(spans))
                if "font-weight: 700" not in spans[i].get_attribute("style")
            ]
            odd_comments = [filtered_comments[i] for i in range(len(filtered_comments)) if i % 2 != 0]

            timestamps = comments_container.find_elements(
                By.XPATH,
                './/span[@style="padding: unset; line-height: 1.3; font-size: 12px; color: rgb(142, 142, 142); white-space: pre-wrap; overflow-wrap: break-word;"]'
            )
            odd_timestamps = [timestamps[i].text for i in range(len(timestamps)) if i % 2 != 0]

            links_divs = comments_container.find_elements(
                By.XPATH,
                './/div[@data-bloks-name="bk.components.Flexbox" and @style="pointer-events: auto; width: 100%;"]'
            )

            for i in range(1, len(links_divs), 2):  # Odd indices
                try:
                    links_divs[i].click()
                    time.sleep(4)
                    post_link = driver.current_url
                    driver.back()
                    time.sleep(4)

                    # After navigating back, re-locate the elements to avoid stale references
                    comments_container = driver.find_element(
                        By.XPATH, '//div[@data-testid="comments_container_non_empty_state"]'
                    )
                    links_divs = comments_container.find_elements(
                        By.XPATH,
                        './/div[@data-bloks-name="bk.components.Flexbox" and @style="pointer-events: auto; width: 100%;"]'
                    )

                    # Convert time_posted to date
                    time_posted = odd_timestamps[i // 2] if i // 2 < len(odd_timestamps) else None
                    if time_posted and 'w' in time_posted:
                        weeks_ago = int(time_posted.replace('w', ''))
                        post_date = (datetime.now() - timedelta(weeks=weeks_ago)).strftime('%Y-%m-%d')
                    else:
                        post_date = None

                    # Append data
                    comments_data.append({
                        "comment": odd_comments[i // 2].strip() if i // 2 < len(odd_comments) else None,
                        "date": post_date,
                        "post_link": post_link
                    })
                except Exception as e:
                    print(f"Error processing div at index {i}: {e}")
            break
        except Exception as e:
            print(f"Error re-fetching elements: {e}")
            break

    json_path = os.path.join(path, "comments.json")
    with open(json_path, "w", encoding="utf-8") as json_file:
        json.dump(comments_data, json_file, ensure_ascii=False, indent=4)

    print(f"Comments data saved at: {json_path}")
    return comments_data