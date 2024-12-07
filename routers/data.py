import asyncio
import datetime
from typing import Annotated
from bson import ObjectId
from fastapi import APIRouter, BackgroundTasks, Form, HTTPException, Request
from models.data import DataEntry
from database import db_instance
import logging
import traceback
import json

from app_scrapers.instagram.main import compile_instagram_account
# from app_scrapers.facebook.main import compile_facebook_report
# from app_scrapers.x.main import compile_x_report
from utils.data_utils import create_data_object, scrape_and_store, get_cases_collection, get_users_collection
from utils.jwt_handler import decode_access_token

router = APIRouter()

# Define scraper functions for supported platforms
PLATFORM_SCRAPERS = {
    "instagram": compile_instagram_account
    # "x": compile_x_report,
    # "facebook": compile_facebook_report
}
@router.post("/scrape")
async def login_user(
    request: Request,
    case: Annotated[str, Form()],
    suspect_name: Annotated[str, Form()],
    platform: Annotated[str, Form()],
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    background_tasks: BackgroundTasks
):
    # Retrieve and validate the token
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    try:
        token = token.split(" ")[1]  # Extract the actual token from 'Bearer <token>'
        payload = decode_access_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid token")
        user_id = ObjectId(payload.get("sub"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error handling token: {str(e)}")

    # Validate the platform and initiate scraping
    if platform not in PLATFORM_SCRAPERS:
        raise HTTPException(status_code=400, detail="Invalid platform")

    scraper_function = PLATFORM_SCRAPERS[platform]

    try:
        # Create a data object and get its ID
        data_id = await create_data_object(user_id, case, username, platform, suspect_name)

        # Add the scraping task to the background
        background_tasks.add_task(scrape_and_store, scraper_function, username, password, platform, data_id)

        return {"message": f"Scraping started for {platform} in the background."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting scraping task: {str(e)}")
    
    
#library of the agent
# @router.get("/datafiles")
# async def get_data_files(request: Request):
#     token = request.headers.get("Authorization")
#     if not token:
#         raise HTTPException(status_code=401, detail="Authorization header missing")
#     try:
#         token = token.split(" ")[1]  # Extract the actual token from 'Bearer <token>'
#         payload = decode_access_token(token)
#         if not payload:
#             raise HTTPException(status_code=401, detail="Invalid token")
#         user_id = payload.get("sub")
#         user_id=ObjectId(user_id)
#     except Exception as e:
#         logging.error(f"Token error: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Error handling token: {str(e)}")
    
    # users_collection = get_users_collection()
    # case_collection = get_cases_collection()

    # user = users_collection.find_one({"_id": user_id})
    # user_cases_ids = user["caseIds"]

    # data = []
    # for case_id in user_cases_ids:
    #   case = case_collection.find({"_id": case_id})
    #   source = []
    #   for data in case[linked_data]:
    #       source.append(data["platform_data"])
    #   case = {
    #       "name": case["case_number"],
    #       "sources": source,
    #       "status": case["status"]
    #       "case_id": case["case_id"]
    #    }
    #   data.append(case)

    # return json.dumps(data, indent=4, default = str)