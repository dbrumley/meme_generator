from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.config import settings
from redis import Redis
import uuid
from app.services.meme_service import process_meme
import logging
import sqlite3
from os.path import isfile


app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

con = sqlite3.connect(':memory:')

# CORS settings
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Redis
redis_client = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

@app.on_event("startup")
async def startup_event():
    """Creates an in-memory database with a user table, and populate it with
    one account"""
    cur = con.cursor()
    cur.execute('''CREATE TABLE users (email text, password text)''')
    cur.execute('''INSERT INTO users VALUES ('me@me.com', '123456')''')
    con.commit()


# SQL injection
@app.get("/login")
async def login(email: str, password: str):
    cur = con.cursor()
    # SQL injection!
    cur.execute("SELECT * FROM users WHERE email = '%s' and password = '%s'" % (email, password))
    return cur.fetchone() is not None

@app.get("/logout")
async def root(email: str):
    return {"message": "Logged out %s!" % email}

@app.get("/attachment")
async def attachment(attachment_name: str):
    attachment_path = 'attachments/' + attachment_name
    if not isfile(attachment_path):
        raise HTTPException(status_code=404, detail="Attachment not found")

    with open(attachment_path) as f:
        return f.readlines()
    
@app.post("/api/create_meme/")
async def create_meme(file: UploadFile = File(...), top_text: str = Form(...), bottom_text: str = Form(...)):    
    task_id = str(uuid.uuid4())
    input_image_path = f"/tmp/{task_id}_{file.filename}"
    output_image_path = f"/tmp/processed_{task_id}_{file.filename}"

    try:
        with open(input_image_path, "wb") as buffer:
            buffer.write(file.file.read())
    except Exception as e:
        logger.error("Error saving uploaded image: %s", str(e))
        raise HTTPException(status_code=500, detail="Error saving uploaded image")

    # Update Redis with initial status and input parameters
    redis_client.hset(task_id, mapping={"status": "processing", "input": input_image_path, "output": output_image_path, "top_text": top_text, "bottom_text": bottom_text})

    # Process the Meme
    try:
        process_meme(task_id, redis_client)
        redis_client.hset(task_id, "status", "completed")
    except Exception as e:
        redis_client.hset(task_id, "status", "failed")
        logger.error("Error processing meme: %s", str(e))
        raise HTTPException(status_code=500, detail="Error processing meme")
    
    return {"task_id": task_id}


@app.get("/api/task_status/{task_id}")
def get_task_status(task_id: str):
    task_info = redis_client.hgetall(task_id)
    if not task_info:
        raise HTTPException(status_code=404, detail="Task not found")

    status = task_info.get(b"status").decode("utf-8")
    return {"task_id": task_id, "status": status}

@app.get("/api/download_meme/{task_id}")
def download_meme(task_id: str):
    task_info = redis_client.hgetall(task_id)
    if not task_info:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task_info.get(b"status").decode("utf-8") != "completed":
        raise HTTPException(status_code=400, detail="Meme processing not completed")

    output_image_path = task_info.get(b"output").decode("utf-8")
    return FileResponse(output_image_path, media_type="image/jpeg")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Meme Generator API"}
