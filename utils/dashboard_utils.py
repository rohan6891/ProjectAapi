import json
from database import db_instance
import os
from datetime import datetime
from collections import defaultdict

def format_instagram_data(Insta_data, suspect_name):
    formatted_output = defaultdict(list)

    # Format Instagram data
    for chat in Insta_data.get('chats', []):
        for message in chat['chat']:
            formatted_output[message['date']].append({
                "platform": "Instagram",
                "type": "chatted",
                "description": f"{suspect_name} chatted with {chat['receiver_name']} on Instagram: '{message['message']}'."
            })

    for post in Insta_data.get('posts', []):
        formatted_output[post['date']].append({
            "platform": "Instagram",
            "type": "posted",
            "description": f"{suspect_name} posted on Instagram with link {post['post_link']}"
        })

    for comment in Insta_data.get('comments', []):
        formatted_output[comment['date']].append({
            "platform": "Instagram",
            "type": "commented",
            "description": f"{suspect_name} commented on Instagram post with link {comment['post_link']}: '{comment['comment']}'"
        })

    # Combine Instagram data into the required format
    combined_output = []
    for date, data in sorted(formatted_output.items(), key=lambda x: datetime.strptime(x[0], "%Y-%m-%d")):
        combined_output.append({"date": date, "data": data})

    return combined_output

def format_twitter_data(X_data, suspect_name):
    formatted_output = defaultdict(list)

    # Format Twitter data
    for chat in X_data.get('chats', []):
        for message in chat['chat']:
            formatted_output[datetime.now().strftime("%Y-%m-%d")].append({
                "platform": "Twitter",
                "type": "chatted",
                "description": f"{suspect_name} chatted with {chat['receiver_name']} on Twitter: '{message['message']}'."
            })

    for tweet in X_data.get('tweets', []):
        formatted_output[datetime.strptime(tweet['date'], "%Y-%m-%d").strftime('%Y-%m-%d')].append({
            "platform": "Twitter",
            "type": "tweeted",
            "description": f"{suspect_name} tweeted on Twitter: '{tweet.get('tweet', 'No tweet text')}'."
        })

    # Combine Twitter data into the required format
    combined_output = []
    for date, data in sorted(formatted_output.items(), key=lambda x: datetime.strptime(x[0], "%Y-%m-%d")):
        combined_output.append({"date": date, "data": data})

    return combined_output

def format_data(Insta_data=None, X_data=None, suspect_name="Suspect"):
    combined_output = []

    if Insta_data:
        combined_output.extend(format_instagram_data(Insta_data, suspect_name))

    if X_data:
        combined_output.extend(format_twitter_data(X_data, suspect_name))

    # Merge data by date if both platforms are provided
    merged_output = defaultdict(list)
    for item in combined_output:
        merged_output[item['date']].extend(item['data'])

    final_output = []
    for date, data in sorted(merged_output.items(), key=lambda x: datetime.strptime(x[0], "%Y-%m-%d")):
        final_output.append({"date": date, "data": data})

    return final_output


async def get_cases_collection():
    return db_instance.get_collection("case_collections")

async def get_data_collection():
    return db_instance.get_collection("data")

def get_raw_data(path, platform):
    path = os.path.join(r"C:\Users\katik\Desktop\SIH\SIH_FINAL\Backend\ProjectAapi\ScraData", path, platform + "_Report.json")
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
        return data




async def get_timeline_data(case_id):
    cases_collection = await get_cases_collection()
    data_collection = await get_data_collection()
    
    # Await the find_one() call to get the actual document
    case_doc = await cases_collection.find_one({"case_number": case_id})
    
    if not case_doc or "linked_data" not in case_doc:
        return []  # Return an empty list if the case document or "linked_data" is missing
    
    raw_data = []
    for data in case_doc["linked_data"]:
        suspect_name = data["suspect_name"]
        platform = data["platform_data"]
        data_doc_id = data["platform_data_id"]
        
        # Await the find_one() call for the data collection
        data_doc = await data_collection.find_one({"_id": data_doc_id})
        
        if not data_doc or not data_doc.get("folder_path"):
            continue
        
        folder_path = data_doc["folder_path"]
        platform_data = get_raw_data(folder_path, platform)
        raw_data.append({
            'suspect_name': suspect_name,
            'platform': platform,
            'data': platform_data
        })
    return raw_data
