import datetime
from typing import Annotated
from bson import ObjectId
from fastapi import APIRouter, BackgroundTasks, Form, HTTPException
from models.data import DataEntry
from database import db_instance
import traceback, logging
import time



from app_scrapers.instagram.main import compile_instagram_account
from app_scrapers.facebook.main import compile_facebook_report
from app_scrapers.x.main import compile_x_report
router = APIRouter()

PLATFORM_SCRAPERS = {
    "instagram": compile_instagram_account,
    "x":compile_x_report,
    "facebook":compile_facebook_report
}



@router.post("/scrape")
async def login_user(case: Annotated[str, Form()],platform: Annotated[str, Form()],username: Annotated[str, Form()], password: Annotated[str, Form()], background_tasks: BackgroundTasks):
    try:
        if platform not in PLATFORM_SCRAPERS:
            raise HTTPException(status_code=400, detail="Invalid platform")
        scraper_function = PLATFORM_SCRAPERS[platform]
        background_tasks.add_task(scrape_and_store, scraper_function, username, password, platform)
        return {"message": f"Scraping started for {platform} in the background."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting scraping task: {str(e)}")
    

def scrape_and_store(scraper_function, username, password, platform):
    try:
        data_folder_path = scraper_function(username, password)
        store_in_mongodb(username, data_folder_path, platform)
    except Exception as e:
        raise Exception(f"Error during scraping {platform}: {str(e)}")

def store_in_mongodb(username, data_folder_path, platform):
    try:
        # Insert the scraping result (folder path and platform) into MongoDB
        data = {
            "username": username,
            "data_folder_path": data_folder_path,
            "platform": platform,
            "timestamp": datetime.utcnow()  # Track when the scraping was done
        }
        # db_instance.scraping_reports.insert_one(data)
        print(data)
    except Exception as e:
        raise Exception(f"Error storing data in MongoDB: {str(e)}")
    

@router.post("/storeData/")
async def store_data(input_data: DataEntry):
    try:
        document = input_data.dict()
        if "_id" not in document:
            raise KeyError("'_id' key is missing from the input document.")
        document["_id"] = ObjectId(document["_id"])
        for entry in document["data"]:
            entry["_id"] = ObjectId(entry["_id"])
            entry["user_id"] = ObjectId(entry["user_id"])
            entry["last_updated"] = entry["last_updated"].isoformat()
            for post in entry.get("posts", []):
                post["created_at"] = post["created_at"].isoformat()
            for tweet in entry.get("tweets", []):
                tweet["date"] = tweet["date"].isoformat()
            for chat in entry.get("chats", []):
                for message in chat["messages"]:
                    message["timestamp"] = message["timestamp"].isoformat()

        db_instance.db.data_collections.insert_one(document)
        return {"message": f"Data stored successfully"}
    except Exception as e:
        detailed_traceback = traceback.format_exc()
        logging.error("An error occurred while processing the request.", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error_message": str(e),
                "error_type": type(e).__name__,
                "traceback": detailed_traceback,
                "context": "An error occurred while converting the input to a MongoDB document."
            }
        )
