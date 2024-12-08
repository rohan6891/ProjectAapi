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
import json

from app_scrapers.x.FuncScrape.tweets import fetch_tweets
from app_scrapers.x.FuncScrape.chats import fetch_chats
from app_scrapers.x.FuncScrape.followers import fetch_followers
from app_scrapers.x.FuncScrape.following import fetch_following
from app_scrapers.x.FuncScrape.chats_json import fetch_chats_json
from app_scrapers.x.FuncScrape.tweets_json import fetch_tweets_json
from app_scrapers.x.FuncScrape.following_json import fetch_following_json
from app_scrapers.x.FuncScrape.followers_json import fetch_followers_json
from app_scrapers.x.FuncScrape.accoount_info import fetch_account_details
from app_scrapers.x.FuncScrape.account_info_json import fetch_account_details_as_json

def create_data_folder(username):
    folder_name = f"Data_{username}"
    folder_path = os.path.join(r"C:\Users\katik\Desktop\SIH\SIH_FINAL\Backend\ProjectAapi\ScraData", "x", folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created directory: {folder_path}")
    else:
        print(f"Directory already exists: {folder_path}")
    return folder_path 

def fetch_username(driver):
    driver.get("https://x.com/home")
    profile_button=WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//a[@aria-label="Profile"]')))
    profile_link = profile_button.get_attribute('href')
    username = profile_link.split("/")[-1]
    return username

def create_title_page(username, pdf_report):
    width, height = A4
    pdf_report.setFont("Times-Roman", 50)
    title_y = height / 2 + 50
    pdf_report.drawCentredString(width / 2, title_y, "X Report")
    text_width = pdf_report.stringWidth("X Report", "Times-Roman", 50)
    underline_x_start = (width - text_width) / 2
    underline_y = title_y - 5
    pdf_report.setLineWidth(1)
    pdf_report.line(underline_x_start, underline_y, underline_x_start + text_width, underline_y)
    pdf_report.line(underline_x_start, underline_y - 3, underline_x_start + text_width, underline_y - 3)
    pdf_report.setFont("Times-Roman", 32)
    username_y = title_y - 50
    pdf_report.drawCentredString(width / 2, username_y, f"Username: {username}")
    pdf_report.showPage()

def login_to_twitter(driver, username, password):
    driver.get("https://x.com/i/flow/login")
    time.sleep(5)
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[autocomplete="username"]'))).send_keys(username)
    driver.find_element(By.XPATH, "//span[text()='Next']").click()
    time.sleep(38)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "password"))).send_keys(password)
    driver.find_element(By.CSS_SELECTOR, 'button[data-testid="LoginForm_Login_Button"]').click()
    time.sleep(8)

def compile_x_report(username, password):
    path=create_data_folder(username)
    report_filename = os.path.join(path, "x_Report.pdf")
    pdf_report = canvas.Canvas(report_filename, pagesize=A4)
    create_title_page(username, pdf_report)

    # Set up Chrome options for headless mode 
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=chrome_options)
    login_to_twitter(driver, username, password)
    if re.fullmatch(r"[^@]+@[\w-]+\.[\w.-]+$", username):
        username = fetch_username(driver)


    #x data in pdf format  
    fetch_account_details(driver, pdf_report, path, password)  
    fetch_tweets(driver, pdf_report, username,path)
    fetch_chats(driver, pdf_report,path)
    fetch_followers(driver, pdf_report, username, path)
    fetch_following(driver, pdf_report, username, path)  
    pdf_report.save()
    print(f"X report saved as: {report_filename}")

    #x data in json format
    driver.maximize_window()
    followers=fetch_followers_json(driver, username,path)
    following=fetch_following_json(driver, username,path)
    tweets=fetch_tweets_json(driver,username,path)
    chats=fetch_chats_json(driver,path)
    account_info=fetch_account_details_as_json(driver, path)
    x_json_data={
        'username':username,
        'account information':account_info,
        'tweets':tweets,
        'chats':chats,
        'followers':followers,
        'following':following
    }
    json_file_path = os.path.join(path, "x_Report.json")
    with open(json_file_path, "w", encoding="utf-8") as json_file:
        json.dump(x_json_data, json_file, ensure_ascii=False, indent=4)
    print(f"X report saved at: {json_file_path}")    
    driver.quit()    
    return f"x/Data_{username}"






