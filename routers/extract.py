from typing import Annotated
from fastapi import APIRouter, Form,Query

from utils.dashboard_utils import get_cases_collection, get_data_collection
from utils.extract_utils import extract_folder_paths


router = APIRouter()

@router.get("/report")
async def create_report(case:Annotated[str,Form()],options: Annotated[list, Form()]):
    cases_collection = await get_cases_collection()
    case_doc = await cases_collection.find_one({"case_number": case})
    folder_paths=extract_folder_paths(case_doc,options)
    return folder_paths

async def get_data_options(case):
    # Fetch the cases collection
    cases_collection = await get_cases_collection()
    data_collection = await get_data_collection()

    # Find the document for the given case number
    case_doc = await cases_collection.find_one({"case_number": case})

    # Initialize the options list
    options = []

    # Dictionary to map suspect names to their respective platforms
    suspect_platform_map = {}

    # Iterate over the linked data
    for data in case_doc["linked_data"]:
        suspect_name = data["suspect_name"]
        platform = data["platform_data"]
        platform_data_id = data["platform_data_id"]

        # Fetch the document from data_collection
        platform_doc = await data_collection.find_one({"_id": platform_data_id})

        # Verify if the document has folder_path not null
        if platform_doc and platform_doc.get("folder_path"):
            # If suspect name already exists in the map, append the platform
            if suspect_name in suspect_platform_map:
                if platform not in suspect_platform_map[suspect_name]:
                    suspect_platform_map[suspect_name].append(platform)
            else:
                # Add suspect name and platform to the map
                suspect_platform_map[suspect_name] = [platform]

    # Convert the map into the desired format
    for suspect_name, platforms in suspect_platform_map.items():
        options.append({"suspect_name": suspect_name, "platform": platforms})

    return options


@router.get("/case_ids")
async def get_case_ids():
    cases_collection = await get_cases_collection()
    data_collection = await get_data_collection()
    case_ids = []

    # Iterate over each document in cases collection
    async for case_doc in cases_collection.find():
        case_number = case_doc.get("case_number")

        # Check linked_data objects
        for data in case_doc.get("linked_data", []):
            platform_data_id = data.get("platform_data_id")

            # Fetch the document from data_collection
            platform_doc = await data_collection.find_one({"_id": platform_data_id})

            # Verify if the document has folder_path not null
            if platform_doc and platform_doc.get("folder_path"):
                case_ids.append(case_number)
                break  # Avoid adding the same case_number multiple times

    return case_ids


@router.get("/options")
async def get_data_options(case: str = Query(...)):
    # Fetch the cases collection
    cases_collection =  await get_cases_collection()
    data_collection = await get_data_collection()

    # Find the document for the given case number
    case_doc = await cases_collection.find_one({"case_number": case})

    # Initialize the options list
    options = []

    # Dictionary to map suspect names to their respective platforms
    suspect_platform_map = {}

    # Iterate over the linked data
    for data in case_doc["linked_data"]:
        suspect_name = data["suspect_name"]
        platform = data["platform_data"]
        platform_data_id = data["platform_data_id"]

        # Fetch the document from data_collection
        platform_doc = await data_collection.find_one({"_id": platform_data_id})

        # Verify if the document has folder_path not null
        if platform_doc and platform_doc.get("folder_path"):
            # If suspect name already exists in the map, append the platform
            if suspect_name in suspect_platform_map:
                if platform not in suspect_platform_map[suspect_name]:
                    suspect_platform_map[suspect_name].append(platform)
            else:
                # Add suspect name and platform to the map
                suspect_platform_map[suspect_name] = [platform]

    # Convert the map into the desired format
    for suspect_name, platforms in suspect_platform_map.items():
        options.append({"suspect_name": suspect_name, "platform": platforms})

    return options