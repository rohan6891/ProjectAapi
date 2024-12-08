import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os
import sys
from selenium.common.exceptions import TimeoutException
from PIL import Image
import re

from app_scrapers.facebook.FuncScrape.chats_json import fetch_chats_as_json
from app_scrapers.facebook.FuncScrape.posts import fetch_posts
from app_scrapers.facebook.FuncScrape.chats import fetch_chats
from app_scrapers.facebook.FuncScrape.posts_json import fetch_posts_as_json
from app_scrapers.facebook.FuncScrape.friends_json import fetch_friends_as_json
from app_scrapers.facebook.FuncScrape.friends import fetch_friends
from app_scrapers.facebook.FuncScrape.personal_info import fetch_personal_info
from app_scrapers.facebook.FuncScrape.personal_info_json import fetch_personal_info_as_json

def create_data_folder(username):
    folder_name = f"Data_{username}"
    folder_path = os.path.join(r"C:\Users\katik\Desktop\SIH\SIH_FINAL\Backend\ProjectAapi\ScraData","facebook", folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created directory: {folder_path}")
    else:
        print(f"Directory already exists: {folder_path}")
    return folder_path 

def fetch_username(driver):
    driver.get("http://www.facebook.com")
    try:
        time.sleep(15)
        username=driver.find_elements(By.TAG_NAME, "ul")[1].find_elements(By.TAG_NAME, "li")[0].find_element(By.TAG_NAME, "span").text
        print(username)
        return username    
    except Exception as e:
        print(f"Error: {e}")
        return None
    
def create_title_page(username, pdf_report):
    width, height = A4
    pdf_report.setFont("Times-Roman", 50)
    title_y = height / 2 + 50
    pdf_report.drawCentredString(width / 2, title_y, "Facebook Report")
    text_width = pdf_report.stringWidth("Facebook Report", "Times-Roman", 50)
    underline_x_start = (width - text_width) / 2
    underline_y = title_y - 5
    pdf_report.setLineWidth(1)
    pdf_report.line(underline_x_start, underline_y, underline_x_start + text_width, underline_y)
    pdf_report.line(underline_x_start, underline_y - 3, underline_x_start + text_width, underline_y - 3)
    pdf_report.setFont("Times-Roman", 32)
    username_y = title_y - 50
    pdf_report.drawCentredString(width / 2, username_y, f"Username: {username}")
    pdf_report.showPage()


def login_facebook(driver, username, password):
    
    driver.get("http://www.facebook.com")
    time.sleep(30)
    user_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='email']")))
    pass_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='pass']")))
    user_input.clear()
    pass_input.clear()
    user_input.send_keys(username)
    pass_input.send_keys(password)
    time.sleep(2)
    login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "login")))
    login_button.click()
    time.sleep(8)
    print(f"Logged in as {username}")

def compile_facebook_report(username, password):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=chrome_options)
    login_facebook(driver, username, password)
    username=fetch_username(driver)
    data_folder_path = create_data_folder(username)
    report_filename = os.path.join(data_folder_path, f"Facebook_Report.pdf")  
    pdf_report = canvas.Canvas(report_filename, pagesize=A4)

    create_title_page(username, pdf_report)

    fetch_posts(driver,pdf_report,username,data_folder_path)
    fetch_chats(driver,pdf_report,data_folder_path)  
    fetch_friends(driver, pdf_report,data_folder_path)
    fetch_personal_info(driver,pdf_report,data_folder_path)
    pdf_report.save()
    print(f"Facebook report saved as: {report_filename}")
    driver.maximize_window()
    personal_info=fetch_personal_info_as_json(driver,data_folder_path)
    chats=fetch_chats_as_json(driver,data_folder_path)
    posts=fetch_posts_as_json(driver, username,data_folder_path)
    friends=fetch_friends_as_json(driver,data_folder_path)
    facebook_data={
        'personal_info':personal_info,
        'posts':posts,
        'chats':chats,
        'friends':friends
    }
    json_file_path = os.path.join(data_folder_path, "Facebook_Report.json")
    with open(json_file_path, "w", encoding="utf-8") as json_file:
        json.dump(facebook_data, json_file, ensure_ascii=False, indent=4)
    print(f"Facebook json report saved at: {json_file_path}")    
    driver.quit()
    return f"facebook/Data_{username}"
