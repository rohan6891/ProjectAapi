import asyncio
import datetime
import bcrypt
from bson import ObjectId
from fastapi import HTTPException
from fastapi.concurrency import run_in_threadpool
from database import db_instance

async def get_users_collection():
    user_agent_collection = db_instance.get_collection("user_agents")  # No need to await here
    return user_agent_collection

async def get_cases_collection():
    user_agent_collection = db_instance.get_collection("case_collections")  # No need to await here
    return user_agent_collection

async def get_data_collection():
    user_agent_collection = db_instance.get_collection("data")  # No need to await here
    return user_agent_collection


async def create_data_object(user_id, case,username, platform, suspect_name):
    users_collection = await get_users_collection()
    data_collection = await get_data_collection()
    cases_collection = await get_cases_collection()

    # Find the user and case documents
    user = await users_collection.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    case_doc = await cases_collection.find_one({"case_number": case})
    if not case_doc:
        raise HTTPException(status_code=404, detail="Case not found")
    user["caseIds"].append(case_doc["_id"])
    # Update suspect name in the case

    if suspect_name not in case_doc["suspect_name"]:
        case_doc["suspect_name"].append(suspect_name)

    # Insert data entry into the data collection
    data = await data_collection.insert_one({
        "username":username,
        "platform": platform,
        "last_updated": None,
        "folder_path": None
    })

    
    case_doc["linked_data"].append({
        "platform_data_id": data.inserted_id,
        "platform_data": platform,
        "linked_at": datetime.datetime.utcnow().isoformat()
    })

    # Perform updates in MongoDB
    await users_collection.update_one({"_id": user_id}, {"$set": {"caseIds": user["caseIds"]}})
    await cases_collection.update_one(
        {"case_number": case},
        {"$set": {"suspect_name": case_doc["suspect_name"], "linked_data": case_doc["linked_data"]}}
    )

    return str(data.inserted_id)  # Return the inserted data ID as a string



async def scrape_and_store(scraper_function, username, password, platform, data_id):
    try:
        # Run scraper function in a separate thread if it's blocking
        data_folder_path = await run_in_threadpool(scraper_function, username, password)
        await store_in_mongodb(data_folder_path, platform, data_id)
    except Exception as e:
        raise Exception(f"Error during scraping {platform}: {str(e)}")


async def store_in_mongodb(data_folder_path, platform, data_id):
    data_collection = await get_data_collection()
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
    """
    Fetch all cases associated with a user based on their `caseIds`.
    """
    users_collection = await get_users_collection()
    user_doc = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")

    case_ids = user_doc["caseIds"]
    return case_ids


async def fetch_case_data(case_id):
    """
    Fetch a single case document by its ID.
    """
    cases_collection = await get_cases_collection()
    case = await cases_collection.find_one({"_id": ObjectId(case_id)})
    return case


async def fetch_platform_data_status(platform_data_id):
    """
    Fetch the status of a platform_data_id from the data collection.
    """
    data_collection = await get_data_collection()
    data_doc = await data_collection.find_one({"_id": ObjectId(platform_data_id)})
    if data_doc["folder_path"] is None:
        return "In Progress"
    return "Completed"


async def build_case_response(user_id):
    """
    Build the final response array for /datafiles route.
    """
    case_ids = await get_user_cases(user_id)
    print(case_ids)
    response = []

    for case_id in case_ids:
        case = await fetch_case_data(case_id)

        case_number = case["case_number"]  # Use case_number instead of document ID
        suspect_names = case["suspect_name"]
        suspect_name = suspect_names[0] if suspect_names else "Unknown"

        linked_data = case["linked_data"]
        for data_entry in linked_data:
            platform_data_id = data_entry["platform_data_id"]
            platform = data_entry["platform_data"]

            # Fetch status for platform_data_id
            status = await fetch_platform_data_status(platform_data_id)

            # Add each source as a separate object in the response
            response.append({
                "name": suspect_name,
                "source": platform,
                "status": status,
                "case_id": case_number,  # Return case_number instead of MongoDB ObjectId
            })

    return response
