from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import auth, brain_dumps, tasks, shopping_items, calendar_events

# Initialize FastAPI app
app = FastAPI(
    title="Klara Backend",
    description="Mental load management for parents",
    version="1.0.0",
)


# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(brain_dumps.router)
app.include_router(tasks.router)
app.include_router(shopping_items.router)
app.include_router(calendar_events.router)


@app.get("/")
def read_root():
    return {"message": "Klara Backend API", "status": "running", "version": "1.0.0"}
