from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import case_dashboard, extract, user, data
import uvicorn
import threading
from utils.data_utils import scraper_runner

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific origins for production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers
)
app.mount("/static", StaticFiles(directory="ScraData"), name="static")

# Register routers
app.include_router(user.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(data.router, prefix="/api/v1/data", tags=["Data"])
app.include_router(extract.router, prefix="/api/v1/extract", tags=["Extract"])
app.include_router(case_dashboard.router,prefix="/api/v1/case_dashboard",tags=["Case_Dashboard"])
"""if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)"""

if __name__ == "__main__":
    # Start the scraper in a separate thread
    scraper_thread = threading.Thread(target=scraper_runner, daemon=True)
    scraper_thread.start()

    # Start the FastAPI server
    uvicorn.run(app, host="127.0.0.1", port=8000)
