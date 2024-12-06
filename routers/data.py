from fastapi import APIRouter, HTTPException
from api.models.data import InputModel
from api.database import db_instance
import traceback, logging

router = APIRouter()

@router.post("/storeData/")
async def store_data(input_data: InputModel):
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
