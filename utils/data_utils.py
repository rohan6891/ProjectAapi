"""import asyncio
import datetime
import json
from bson import ObjectId
from fastapi import HTTPException
from fastapi.concurrency import run_in_threadpool
from database import db_instance

async def get_cases_collection():
    return db_instance.get_collection("case_collections")

async def get_users_collection():
    return db_instance.get_collection("user_agents")


async def create_data_object(user_id, case, username, platform, suspect_name):
    users_collection = await get_users_collection()
    data_collection = db_instance.get_collection("data")
    cases_collection = db_instance.get_collection("case_collections")

    # Find the user and case documents
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    case_doc = await cases_collection.find_one({"case_number": case})
    if not case_doc:
        raise HTTPException(status_code=404, detail="Case not found")

    # Add case ID to user if not already present
    if case_doc["_id"] not in user["caseIds"]:
        user["caseIds"].append(case_doc["_id"])

    # Add suspect name to case document if not already present
    if suspect_name not in case_doc["suspect_name"]:
        case_doc["suspect_name"].append(suspect_name)

    # Check if data entry for the username and platform already exists
    existing_data = await data_collection.find_one({"username": username, "platform": platform})
    if existing_data:
        # Update last_updated to None for tracking purposes
        await data_collection.update_one(
            {"_id": existing_data["_id"]},
            {"$set": {"last_updated": None}}
        )
        
        data_id = existing_data["_id"]
    else:
        # Create a new data entry
        new_data = await data_collection.insert_one({
            "username": username,
            "platform": platform,
            "last_updated": None,
            "folder_path": None
        })
        data_id = new_data.inserted_id

    # Check if platform_data_id already exists in linked_data
    linked_data_entry = next(
        (entry for entry in case_doc["linked_data"] if entry["platform_data_id"] == data_id),
        None
    )
    if linked_data_entry:
        # Update linked_at timestamp
        linked_data_entry["linked_at"] = datetime.datetime.utcnow().isoformat()
    else:
        # Add a new linked_data entry
        case_doc["linked_data"].append({
            "suspect_name":suspect_name,
            "platform_data_id": data_id,
            "platform_data": platform,
            "linked_at": datetime.datetime.utcnow().isoformat()
        })

    # Perform atomic updates in MongoDB
    await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"caseIds": user["caseIds"]}}
    )
    await cases_collection.update_one(
        {"case_number": case},
        {
            "$set": {
                "suspect_name": case_doc["suspect_name"],
                "linked_data": case_doc["linked_data"]
            }
        }
    )

    return str(data_id)  # Return the data ID as a string


async def scrape_and_store(scraper_function, username, password, platform, data_id):
    try:
        # Run scraper function in a separate thread if it's blocking
        data_folder_path = await run_in_threadpool(scraper_function, username, password)
        await store_in_mongodb(data_folder_path, platform, data_id)
    except Exception as e:
        raise Exception(f"Error during scraping {platform}: {str(e)}")


async def store_in_mongodb(data_folder_path, platform, data_id):
    data_collection = db_instance.get_collection("data")
    try:
        data = {
            "folder_path": data_folder_path,
            "last_updated": datetime.datetime.utcnow()
        }
        # Update the document in MongoDB
        await data_collection.update_one({"_id": ObjectId(data_id)}, {"$set": data})
        print(f"Stored data for platform {platform}: {data}")
    except Exception as e:
        raise Exception(f"Error storing data in MongoDB: {str(e)}")


async def get_user_cases(user_id):
    
    #Fetch all cases associated with a user based on their `caseIds`.
    
    users_collection = await get_users_collection()
    user_doc = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")

    return user_doc["caseIds"]


async def fetch_case_data(case_id):
    
    #Fetch a single case document by its ID.
    
    cases_collection = db_instance.get_collection("case_collections")
    return await cases_collection.find_one({"_id": ObjectId(case_id)})


async def fetch_platform_data_status(platform_data_id):
    
    #Fetch the status of a platform_data_id from the data collection.
    
    data_collection = db_instance.get_collection("data")
    data_doc = await data_collection.find_one({"_id": ObjectId(platform_data_id)})
    return "In Progress" if data_doc["folder_path"] is None else "Completed"


async def build_case_response(user_id):
    
    #Build the final response array for /datafiles route.
    
    case_ids = await get_user_cases(user_id)
    response = []

    for case_id in case_ids:
        case = await fetch_case_data(case_id)
        case_number = case["case_number"]

        for data_entry in case["linked_data"]:
            platform_data_id = data_entry["platform_data_id"]
            platform = data_entry["platform_data"]
            suspect_name=data_entry["suspect_name"]
            # Fetch status for platform_data_id
            status = await fetch_platform_data_status(platform_data_id)

            # Add each source as a separate object in the response
            response.append({
                "name": suspect_name,
                "source": platform,
                "status": status,
                "case_id": case_number
            })

    return json.dumps(response)
"""
import threading
import asyncio
from datetime import datetime
import json
from bson import ObjectId
from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from database import db_instance

app = FastAPI()

# Define your collections
def get_cases_collection():
    return db_instance.get_collection("case_collections")
def get_users_collection():
    return db_instance.get_collection("user_agents")

# Check if case exists
async def check_case(case):
    cases_collection = get_cases_collection()
    try:
        return bool(await cases_collection.find_one({"case_number": case}))
    except Exception as e:
        print(f"Error checking case: {e}")
        return False

# Create a new case
async def create_case(case, description, nia_officer, title, cio_officer, eo_officer, eo_designation, suspect_name):
    cases_collection =get_cases_collection()
    new_case = {
        "case_number": case,
        "title": title,
        "description": description or "",
        "niaOfficer": nia_officer,
        "cio_name": cio_officer,
        "eo_name": eo_officer,
        "eo_designation": eo_designation,
        "suspect_name": [suspect_name] if suspect_name else [],  # Ensure suspect_name is a list
        "linked_data": []
    }
    
    if suspect_name not in new_case["suspect_name"]:
        new_case["suspect_name"].append(suspect_name)

    try:
        result =await cases_collection.insert_one(new_case)
        print(f"New case inserted with ID: {result.inserted_id}")
    except Exception as e:
        print(f"Error creating case: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating case: {str(e)}")

# Create or update data object
async def create_data_object(user_id, case, username, platform, suspect_name):
    users_collection = get_users_collection()
    data_collection = db_instance.get_collection("data")
    cases_collection = get_cases_collection()

    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    case_doc = await cases_collection.find_one({"case_number": case})
    if not case_doc:
        raise HTTPException(status_code=404, detail="Case not found")

    # Add case ID to user
    await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$addToSet": {"caseIds": case_doc["_id"]}}
    )

    # Create or update data entry
    existing_data = await data_collection.find_one({"username": username, "platform": platform})
    if existing_data:
        await data_collection.update_one(
            {"_id": existing_data["_id"]},
            {"$set": {"last_updated": None, "folder_path": None}}
        )
        data_id = existing_data["_id"]
    else:
        new_data = await data_collection.insert_one({
            "username": username,
            "platform": platform,
            "last_updated": None,
            "folder_path": None
        })
        data_id = new_data.inserted_id

    # Check if the platform_data_id already exists in the linked_data
    if any(data.get("platform_data_id") == data_id for data in case_doc.get("linked_data", [])):
        # If the platform_data_id exists, update the document in the data collection
        await data_collection.update_one(
            {"_id": data_id},
            {"$set": {"last_updated": None, "folder_path": None}}
        )
    else:
        # Update linked_data in case document
        await cases_collection.update_one(
            {"_id": case_doc["_id"]},
            {
                "$addToSet": {
                    "linked_data": {
                        "suspect_name": suspect_name,
                        "platform_data_id": data_id,
                        "platform": platform,
                        "linked_at": datetime.now().isoformat()
                    }
                }
            }
        )

    return str(data_id)


# Scrape and store
async def scrape_and_store(scraper_function, username, password, platform, data_id):
    data_collection = db_instance.get_collection("data")
    try:
        data_folder_path = await run_in_threadpool(scraper_function, username, password)
        await data_collection.update_one(
            {"_id": ObjectId(data_id)},
            {
                "$set": {
                    "folder_path": data_folder_path,
                    "last_updated": datetime.now()
                }
            }
        )
    except Exception as e:
        raise Exception(f"Error during scraping {platform}: {str(e)}")

# Fetch user cases
async def get_user_cases(user_id):
    users_collection =get_users_collection()
    user_doc = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    return user_doc["caseIds"]

# Fetch case data
async def fetch_case_data(case_id):
    cases_collection=get_cases_collection()
    return await cases_collection.find_one({"_id": ObjectId(case_id)})

# Scraping runner
async def scraper_runner(scraper_function, username, password, platform, data_id):
    try:
        await scrape_and_store(scraper_function, username, password, platform, data_id)
    except Exception as e:
        print(f"Error in scraping runner: {e}")
