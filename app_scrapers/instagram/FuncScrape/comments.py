import os
import time
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from selenium.webdriver.common.by import By
from app_scrapers.instagram.FuncScrape.pdf_utils import create_title_page, scale_image

def fetch_comments(driver, pdf_report,f_upath):
    """Fetches comments from Instagram and adds them to the PDF report."""
    # Navigate to the Comments section
    driver.get("https://www.instagram.com/your_activity/interactions/comments")  # Update this URL if needed
    time.sleep(6)

    # Create directory for saving screenshots
    path = os.path.join(f_upath, "Comments")

    os.makedirs(path, exist_ok=True)
    create_title_page(pdf_report, "COMMENTS")

    # Variable to keep track of the number of screenshots taken
    screenshot_index = 0
    scroll_pause_time = 5  # Adjust if needed

    # Scrollable div and comment logic
    scrollable_div = driver.find_element(By.XPATH, '//div[@data-bloks-name="bk.components.Collection"]')

    # Initialize tracking of comments
    last_comment_count = 0
    no_new_comments_counter = 0  # Track when no new comments are found

    while True:
        # Find the div containing the comments
        comments_container = driver.find_element(By.XPATH, '//div[@data-testid="comments_container_non_empty_state"]')
        comments = comments_container.find_elements(By.XPATH, './/div[@data-testid="post_collection_item"]')

        # Take a screenshot of the entire page
        screenshot_path = os.path.join(path, f"comments_screenshot_{screenshot_index}.png")
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved at: {screenshot_path}")

        # Check if the number of comments has increased
        new_comment_count = len(comments)

        if new_comment_count > last_comment_count:
            last_comment_count = new_comment_count  # Update the last comment count
            no_new_comments_counter = 0  # Reset counter when new comments are found
        else:
            no_new_comments_counter += 1  # Increment when no new comments are found

        # Break if no new comments have appeared for 2 consecutive attempts
        if no_new_comments_counter >= 2:  # Adjust this threshold as needed
            print("No new comments found. Stopping scrolling.")
            break

        # Scroll down the div to load more comments
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
        time.sleep(scroll_pause_time)
        screenshot_index += 1  # Increment the screenshot index for the next screenshot


    # Add all screenshots to the PDF
    for i in range(screenshot_index):
        img_path = os.path.join(path, f"comments_screenshot_{i}.png")
        img = Image.open(img_path)
        img_pdf_width, img_pdf_height = scale_image(img, A4[0] - 60, A4[1] - 60)  # Adjust margins
        x = (A4[0] - img_pdf_width) / 2
        y = (A4[1] - img_pdf_height) / 2
        pdf_report.drawImage(img_path, x, y, width=img_pdf_width, height=img_pdf_height)
        pdf_report.showPage()

    print(f"Comments added to the PDF.")
