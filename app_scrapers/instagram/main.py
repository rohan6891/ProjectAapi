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
from datetime import datetime
import requests
from PIL import Image



from app_scrapers.instagram.FuncScrape.account_info import fetch_account_info
from app_scrapers.instagram.FuncScrape.saved_posts import fetch_saved_posts
from app_scrapers.instagram.FuncScrape.tagged_posts import fetch_tagged_posts
from app_scrapers.instagram.FuncScrape.posts import fetch_posts
from app_scrapers.instagram.FuncScrape.comments import fetch_comments
from app_scrapers.instagram.FuncScrape.likes import fetch_likes
from app_scrapers.instagram.FuncScrape.chats import fetch_chats
from app_scrapers.instagram.FuncScrape.followers import fetch_followers
from app_scrapers.instagram.FuncScrape.following import fetch_following

from app_scrapers.instagram.FuncScrape.account_info_json import fetch_account_info_as_json
from app_scrapers.instagram.FuncScrape.followers_json import fetch_followers_as_json
from app_scrapers.instagram.FuncScrape.following_json import fetch_following_as_json
from app_scrapers.instagram.FuncScrape.comments_json import fetch_comments_as_json
from app_scrapers.instagram.FuncScrape.posts_json import fetch_posts_as_json
from app_scrapers.instagram.FuncScrape.tagged_posts_json import fetch_tagged_posts_as_json
from app_scrapers.instagram.FuncScrape.saved_posts_json import fetch_saved_posts_as_json
from app_scrapers.instagram.FuncScrape.chats_json import fetch_chats_as_json


def create_data_folder(username):
    folder_name = f"Data_{username}"
    folder_path = os.path.join(r"C:\Users\katik\Desktop\SIH\SIH_FINAL\Backend\ProjectAapi\ScraData", "instagram", folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created directory: {folder_path}")
    else:
        print(f"Directory already exists: {folder_path}")
    return folder_path    

def create_title_page(username, pdf_report):
    width, height = A4
    pdf_report.setFont("Times-Roman", 50)
    title_y = height / 2 + 50
    pdf_report.drawCentredString(width / 2, title_y, "Instagram Report")
    text_width = pdf_report.stringWidth("Instagram Report", "Times-Roman", 50)
    underline_x_start = (width - text_width) / 2
    underline_y = title_y - 5
    pdf_report.setLineWidth(1)
    pdf_report.line(underline_x_start, underline_y, underline_x_start + text_width, underline_y)
    pdf_report.line(underline_x_start, underline_y - 3, underline_x_start + text_width, underline_y - 3)
    pdf_report.setFont("Times-Roman", 32)
    username_y = title_y - 50
    pdf_report.drawCentredString(width / 2, username_y, f"Username: {username}")
    pdf_report.showPage()

def login_instagram(driver, username, password):
    driver.get("http://www.instagram.com")
    time.sleep(6)
    user_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']")))
    pass_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))
    user_input.clear()
    pass_input.clear()
    user_input.send_keys(username)
    pass_input.send_keys(password)
    time.sleep(2)
    login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
    login_button.click()
    time.sleep(8)
    print(f"Logged in as {username}")

def compile_instagram_account(username, password):
    path=create_data_folder(username)
    # report_filename = os.path.join(path, "instagram_Report.pdf")
    # pdf_report = canvas.Canvas(report_filename, pagesize=A4)
    # create_title_page(username, pdf_report)

    # chrome_options = Options()
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--window-size=1920,1080")
    
    # driver = webdriver.Chrome(options=chrome_options)
    # login_instagram(driver, username, password)

    # fetch_account_info(driver,pdf_report,username,path)
    # fetch_posts(driver, pdf_report,username,path)
    # fetch_followers(driver,pdf_report,username,path)
    # fetch_following(driver,pdf_report,username,path)
    # fetch_chats(driver,pdf_report,path)
    # fetch_comments(driver, pdf_report,path)
    # fetch_likes(driver, pdf_report,path)
    # fetch_saved_posts(driver, pdf_report,username,path)
    # fetch_tagged_posts(driver, pdf_report,username,path)
    # pdf_report.save()
    # print(f"Instagram pdf report saved as: {report_filename}")

    # driver.maximize_window()
    # account_info=fetch_account_info_as_json(driver,username,path)
    # posts=fetch_posts_as_json(driver,username,path)
    # tagged_posts=fetch_tagged_posts_as_json(driver,username,path)
    # saved_posts=fetch_saved_posts_as_json(driver,username,path)
    # followers=fetch_followers_as_json(driver,username,path)
    # following=fetch_following_as_json(driver,username,path)
    # chats=fetch_chats_as_json(driver,username,path)
    # comments=fetch_comments_as_json(driver,path)
    

    # instagram_data={
    #     'account_info':account_info,
    #     'posts':posts,
    #     'chats':chats,
    #     'saved_posts':saved_posts,
    #     'tagged_posts':tagged_posts,
    #     'comments':comments,
    #     'followers':followers,
    #     'following':following
    # }
    # json_file_path = os.path.join(path, "Instagram_Report.json")
    # with open(json_file_path, "w", encoding="utf-8") as json_file:
    #     json.dump(instagram_data, json_file, ensure_ascii=False, indent=4)
    # print(f"Instagram json report saved at: {json_file_path}")    
    # driver.quit()
    return f"instagram/Data_{username}"
