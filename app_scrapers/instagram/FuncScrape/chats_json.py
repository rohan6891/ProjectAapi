import os
import sys
import traceback
import json
from datetime import datetime
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Global Variables
headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 105.0.0.11.118 (iPhone11,8; iOS 12_3_1; en_US; en-US; scale=2.00; 828x1792; 165586599)"
}

SESSIONID = None
REQUESTS_AMMOUNT = 0
MEMBERS = {}

def get_session_id(driver):
    time.sleep(5)

    # Get cookies
    cookies = driver.get_cookies()
    session_id = None

    # Find the 'sessionid' cookie
    for cookie in cookies:
        if cookie['name'] == 'sessionid':
            session_id = cookie['value']
            break

    if not session_id:
        raise RuntimeError("Session ID not found in cookies.")

    print(f"Session ID: {session_id}")
    return session_id

def get_request(url, headers, cookies):
    response = requests.get(url, headers=headers, cookies=cookies)
    global REQUESTS_AMMOUNT
    REQUESTS_AMMOUNT += 1
    if response.status_code == 429:
        raise RuntimeError("Rate limited by server.")
    try:
        return response.json()
    except json.JSONDecodeError:
        print(response.text)
        return None

def reverse_list(target_list):
    return list(reversed(target_list))

def get_threads():
    url = "https://i.instagram.com/api/v1/direct_v2/inbox/?persistentBadging=true&folder=&thread_message_limit=1&limit=200"
    cookies = {"sessionid": SESSIONID}
    response = get_request(url, headers, cookies)
    threads = response["inbox"]["threads"]
    thread_map = {}
    for thread in threads:
        if thread.get("is_group"):
            name = thread["thread_title"]
        else:
            name = thread["users"][0]["full_name"]
        thread_map[thread["thread_id"]] = name
    return thread_map

def get_messages(thread_id):
    messages = []
    current_cursor = ""
    while True:
        url = f"https://i.instagram.com/api/v1/direct_v2/threads/{thread_id}/?cursor={current_cursor}"
        cookies = {"sessionid": SESSIONID}
        response = get_request(url, headers, cookies)
        thread = response.get("thread", {})
        items = thread.get("items", [])
        messages.extend(items)
        current_cursor = thread.get("oldest_cursor")
        if not current_cursor:
            break
    global MEMBERS
    for user in thread.get("users", []):
        MEMBERS[user["pk"]] = user["full_name"]
    return messages

def parse_messages_to_json(thread_name, username, messages):
    chat = []
    for message in reverse_list(messages):
        sender = MEMBERS.get(message['user_id'], username if message['user_id'] not in MEMBERS else MEMBERS[message['user_id']])
        content = ""

        if message['item_type'] == 'text':
            content = message['text']
        elif message['item_type'] == 'media':
            media = message['media']
            if media['media_type'] == 1:
                content = f"Photo: {media['image_versions2']['candidates'][0]['url']}"
            elif media['media_type'] == 2:
                content = f"Video: {media['video_versions'][0]['url']}"
        elif message['item_type'] == 'voice_media':
            content = f"Voice message: {message['voice_media']['media']['audio']['audio_src']}"
        elif message['item_type'] == 'raven_media':
            content = "Temporary photo or video (might have expired)"
        else:
            content = message['item_type']

        timestamp = datetime.fromtimestamp(float(message["timestamp"]) / 1e6).strftime('%Y-%m-%d %H:%M:%S')
        chat.append({"sender": sender, "message": content, "timestamp": timestamp})

    return {"receiver_name": thread_name, "chat": chat}

def fetch_chats_as_json(driver, username, f_upath):
    global SESSIONID
    SESSIONID = get_session_id(driver)

    threads = get_threads()
    print("Fetching chats for the following threads:")
    all_chats = []
    for thread_id, thread_name in threads.items():
        print(f"- {thread_name} ({thread_id})")
        messages = get_messages(thread_id)
        parsed_chat = parse_messages_to_json(thread_name, username, messages)
        all_chats.append(parsed_chat)

    output_dir = os.path.join(f_upath, "Chats")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "chats.json")

    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(all_chats, json_file, ensure_ascii=False, indent=4)

    print(f"Chats have been saved to {output_path}")
    return all_chats
