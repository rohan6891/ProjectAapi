import os
import time
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app_scrapers.instagram.FuncScrape.pdf_utils import create_title_page, scale_image

def fetch_posts(driver, pdf_report, username,f_upath):
    """Fetches posts from Instagram and adds them to the PDF report."""
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

    # Loop through all anchor tags and collect links to Instagram posts
    for a in a_tags:
        href = a.get_attribute('href')
        if username+'/p/' in href and href not in post_links:
            post_links.append(href)

    print(f'Found {len(post_links)} posts.')

    path = os.path.join(f_upath,"Posts")
    os.makedirs(path, exist_ok=True)
    create_title_page(pdf_report, "POSTS")
    width, height = A4
    margin = 30
    for counter, post_link in enumerate(post_links, start=1):
        try:
            driver.get(post_link)
            time.sleep(3)

            screenshot_path = os.path.join(path, f"post_{counter}.png")
            driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved for post {counter}.")

            img = Image.open(screenshot_path)
            img_pdf_width, img_pdf_height = scale_image(img, width - 2 * margin, height - 2 * margin)
            x = (width - img_pdf_width) / 2
            y = (height - img_pdf_height) / 2
            pdf_report.drawImage(screenshot_path, x, y, width=img_pdf_width, height=img_pdf_height)
            pdf_report.showPage()
            i=2
            while True:
                try:
                    next_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Next"]')))
                    next_button.click()
                    time.sleep(2)

                    screenshot_path = os.path.join(path, f"post_{counter}_{i}.png")
                    driver.save_screenshot(screenshot_path)
                    print(f"Screenshot saved for post {counter} (next).")

                    img = Image.open(screenshot_path)
                    img_pdf_width, img_pdf_height = scale_image(img, width - 2 * margin, height - 2 * margin)
                    pdf_report.drawImage(screenshot_path, x, y, width=img_pdf_width, height=img_pdf_height)
                    pdf_report.showPage()
                    i+=1
                except Exception:
                    break

        except Exception as e:
            print(f"Error processing post {counter}: {e}")
            continue
