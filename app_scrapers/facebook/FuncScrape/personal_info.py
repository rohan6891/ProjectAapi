import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PIL import Image
from FuncScrape.pdf_utils import create_title_page, scale_image

def fetch_personal_info(driver, pdf_report, output_path):
    """
    Extracts personal information from the "About Contact and Basic Info" section of a Facebook profile
    and takes a screenshot of the section to be added to a PDF.
    Scrolls 400 pixels to capture the information in the viewport.

    Args:
        driver: Selenium WebDriver instance.
        pdf_report: ReportLab PDF canvas object for adding pages.
        output_path: Directory path to save screenshots and PDF.
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

    # Scroll 400 pixels to bring the contact info section into the viewport
    try:
        driver.execute_script("window.scrollBy(0, 400);")
        time.sleep(2)  # Wait for the page to settle after scrolling
        print("Scrolled 400 pixels.")
    except Exception as e:
        print(f"Error during scrolling: {e}")
        return

    # Capture screenshot after scrolling
    try:
        output_path = os.path.join(output_path, "Personal_info")
        os.makedirs(output_path, exist_ok=True)
        create_title_page(pdf_report, "PERSONAL INFORMATION")
        
        screenshot_path = os.path.join(output_path, "contact_info_screenshot.png")
        driver.save_screenshot(screenshot_path)
        print(f"Saved screenshot: {screenshot_path}")

        # Add to PDF
        width, height = A4
        margin = 30
        img = Image.open(screenshot_path)
        img_pdf_width, img_pdf_height = scale_image(img, width - 2 * margin, height - 2 * margin)
        x = (width - img_pdf_width) / 2
        y = (height - img_pdf_height) / 2
        pdf_report.drawImage(screenshot_path, x, y, width=img_pdf_width, height=img_pdf_height)
        pdf_report.showPage()
    except Exception as e:
        print(f"Error taking screenshot or adding to PDF: {e}")
        return

    # Return to the main profile page
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(2)
    print("Finished capturing and adding personal info screenshot to PDF.")
