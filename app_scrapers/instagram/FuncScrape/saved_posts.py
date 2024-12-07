from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from app_scrapers.instagram.FuncScrape.pdf_utils import create_title_page, scale_image

def fetch_saved_posts(driver, pdf_report, username,f_upath):
    """Fetches saved posts of a user and adds them to the PDF report."""
    saved_posts_url = f"https://www.instagram.com/{username}/saved/"
    driver.get(saved_posts_url)
    time.sleep(6)

    # Check for the presence of the anchor tag with aria-label="All posts"
    try:
        all_posts_link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//a[@aria-label="All posts"]'))
        )
        # Extract the href and navigate to that page
        all_posts_url = all_posts_link.get_attribute('href')
        driver.get(all_posts_url)
        time.sleep(6)  # Wait for the page to load
    except Exception as e:
        print(f"Could not find 'All posts' link: {e}")
        return

    # Scroll the page to load more posts
    n_scrolls = 2
    for _ in range(n_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    time.sleep(4)

    # Find and collect post links from article tags
    post_links = []
    articles = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, 'article'))
    )

    for article in articles:
        a_tags = article.find_elements(By.TAG_NAME, 'a')
        for a in a_tags:
            href = a.get_attribute('href')
            if href and '/p/' in href and href not in post_links:
                post_links.append(href)

    print(f'Found {len(post_links)} saved posts.')

    # Prepare folder for saving screenshots
    path = os.path.join(f_upath, "Saved_Posts")
    os.makedirs(path, exist_ok=True)

    # Create title page
    create_title_page(pdf_report, "SAVED POSTS")

    # Iterate over each post link and take screenshots
    for counter, post_link in enumerate(post_links, start=1):
        try:
            driver.get(post_link)
            time.sleep(3)

            # Save screenshot
            screenshot_path = os.path.join(path, f"post_{counter}.png")
            driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved for saved post {counter}.")

            # Open the image and scale it to fit the PDF
            img = Image.open(screenshot_path)
            img_pdf_width, img_pdf_height = scale_image(img, A4[0] - 2 * 30, A4[1] - 2 * 30)
            x = (A4[0] - img_pdf_width) / 2
            y = (A4[1] - img_pdf_height) / 2
            pdf_report.drawImage(screenshot_path, x, y, width=img_pdf_width, height=img_pdf_height)
            pdf_report.showPage()
            i=2
            # Handle carousel posts (multiple images in one post)
            while True:
                try:
                    next_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Next"]')))
                    next_button.click()
                    time.sleep(2)

                    screenshot_path = os.path.join(path, f"post_{counter}_{i}.png")
                    driver.save_screenshot(screenshot_path)
                    print(f"Screenshot saved for saved post {counter} (next).")

                    img = Image.open(screenshot_path)
                    img_pdf_width, img_pdf_height = scale_image(img, A4[0] - 2 * 30, A4[1] - 2 * 30)
                    pdf_report.drawImage(screenshot_path, x, y, width=img_pdf_width, height=img_pdf_height)
                    pdf_report.showPage()
                    i+=1
                except Exception:
                    break

        except Exception as e:
            print(f"Error processing saved post {counter}: {e}")
            continue
