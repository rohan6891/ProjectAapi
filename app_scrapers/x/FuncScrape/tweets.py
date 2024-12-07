from selenium.webdriver.common.by import By
from PIL import Image
import time
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from FuncScrape.pdf_utils import create_title_page
from FuncScrape.pdf_utils import scale_image
import os

def fetch_tweets(driver, pdf_report,username,f_upath):
    profile_url = f"https://x.com/{username}"
    driver.get(profile_url)
    time.sleep(5)
    path = os.path.join(f_upath,"Tweets")
    os.makedirs(path, exist_ok=True)
    create_title_page(pdf_report, "TWEETS")
    # Add title page for chats
    width, height = A4
    tweet_links = []
    n_scrolls = 2
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
    
    for index, tweet_link in enumerate(tweet_links):
        driver.get(tweet_link)
        time.sleep(5)
        screenshot_path = os.path.join(path, f"tweet_{index + 1}.png")
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved for Tweet {index + 1}.")

        img = Image.open(screenshot_path)
        img_pdf_width, img_pdf_height = scale_image(img, width - 2 * 30, height - 2 * 30)
        x = (width - img_pdf_width) / 2
        y = (height - img_pdf_height) / 2
        pdf_report.drawImage(screenshot_path, x, y, width=img_pdf_width, height=img_pdf_height)
        pdf_report.showPage()