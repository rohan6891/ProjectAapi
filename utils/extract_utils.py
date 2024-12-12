from tkinter import Canvas
from app_scrapers.facebook.main import create_title_page
from database import db_instance
import os
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
async def get_cases_collection():
    return db_instance.get_collection("case_collections")

async def get_data_collection():
    return db_instance.get_collection("data")

async def extract_folder_paths(case_doc, options: list[dict]): 
    data_collection = await get_data_collection()
    folder_paths = [] 
    linked_data = case_doc["linked_data"]
    for option in options: 
        if isinstance(option, str):
            # Attempt to parse the string to a dictionary
            try:
                option = json.loads(option)
            except json.JSONDecodeError as e:
                raise ValueError(f"Option string could not be parsed to a dictionary: {option}, error: {str(e)}")

        # if not isinstance(option, dict):
        #     raise ValueError(f"Option is not a dictionary: {option}")
        for i in range(len(option)):
            suspect_name = option[i]["suspect_name"]
            platforms = option[i]["platform"]

            if not isinstance(platforms, list):
                raise ValueError(f"Platforms should be a list: {platforms}")

            for platform in platforms:
                for data in linked_data:
                    if data["suspect_name"] == suspect_name and data["platform_data"] == platform:
                        # Retrieve the document from the data collection using platform_data_id
                        platform_data_id = data["platform_data_id"]
                        document = await data_collection.find_one({"_id": platform_data_id})

                        # Access the folder_path from the document and append it to the array
                        if document and "folder_path" in document:

                            folder_paths.append(document["folder_path"])

    return folder_paths



# def create_reports(case,data,title, description, nia_officer, cio, eo, eo_designation, created_at):
#     path=r"C:\Users\katik\Desktop\SIH\SIH_FINAL\Backend\ProjectAapi\Reports"
#     report_filename = os.path.join(path, f"${case}_Report.pdf")
#     pdf = Canvas.Canvas(report_filename, pagesize=A4)

#     pdf_report=create_title_page(pdf,case,title,)
#     for obj in data:
#         suspect_name=obj["suspect_name"]
#         folder_paths=obj["folder_paths"]
#         for folder in folder_paths:
#             username=folder.split("/")[1]
#             platform=folder.split("/")[0]
#             if platform=="instagram":
#                 generate_instagarm_report(pdf,username,)


