from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os, uuid, json
from rq import Queue
from redis import Redis

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
r = Redis(host=os.getenv("REDIS_HOST", "redis"), port=6379, db=0)
q = Queue("batch_jobs", connection=r)

@app.post("/start")
def start_job(input_param: str):
    job_id = str(uuid.uuid4())
    q.enqueue("tasks.process_job", input_param, job_id)
    return {"job_id": job_id}

@app.get("/progress/{job_id}")
def progress(job_id: str):
    progress = r.get(f"progress:{job_id}")
    return {"progress": int(progress) if progress else 0}