from typing import Annotated
from fastapi import APIRouter, Form, HTTPException, Depends, Request
from utils.dashboard_utils import format_data, format_instagram_data, format_twitter_data, get_timeline_data
import json

router = APIRouter()
@router.get("/timelines")
async def get_data(request: Request):
    case=request.headers.get("case")
    data_docs=await get_timeline_data(case)
    formated_data={
        'x':None,
        'instagram':None 
    }
    # return data_docs
    print(data_docs)
    for data in data_docs:
        if data['platform']=='x':
            formated_data['x']=format_twitter_data(data["data"], data["suspect_name"])
        elif data['platform']=='instagram':
            formated_data['instagram']=format_instagram_data(data["data"], data["suspect_name"])
    # print("formatted data:",formated_data['instagram'])
    return formated_data



