from database import db_instance

# Define your collections
async def get_cases_collection():
    return db_instance.get_collection("case_collections")

async def get_data_collection():
    return db_instance.get_collection("data")

async def extract_folder_paths(case_doc, options):
    data_collection =await get_data_collection()
    linked_data = case_doc["linked_data"]
    folder_paths = []
    for option in options:
        suspect_name = option["suspect_name"]
        platforms = option["platform"]
        for platform in platforms:
            for data in linked_data:
                if data["suspect_name"] == suspect_name and data["platform_data"] == platform:
                    # Retrieve the document from the data collection using platform_data_id
                    platform_data_id = data["platform_data_id"]["$oid"]
                    document = await data_collection.find_one({"_id": platform_data_id})

                    # Access the folder_path from the document and append it to the array
                    if document and "folder_path" in document:
                        folder_paths.append(document["folder_path"])

    return folder_paths