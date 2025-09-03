from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import os, uuid, json
from rq import Queue
from redis import Redis
from fastapi.responses import FileResponse

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

# Rutas de carpetas compartidas
INPUT_DIR = "/srv/shared/input"
OUTPUT_DIR = "/srv/shared/output"

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())
    filename = f"{job_id}.txt"
    file_path = os.path.join(INPUT_DIR, filename)

    # Guardar archivo subido en la carpeta compartida
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Enviar tarea al batch
    q.enqueue("tasks.process_job", filename, job_id)

    return {"job_id": job_id, "filename": filename}


@app.get("/progress/{job_id}")
def progress(job_id: str):
    progress = r.get(f"progress:{job_id}")
    return {"progress": int(progress) if progress else 0}


@app.get("/result/{job_id}")
def get_result(job_id: str):
    result_file = os.path.join(OUTPUT_DIR, f"{job_id}.txt")
    if os.path.exists(result_file):
        return FileResponse(
            result_file,
            media_type="text/plain",
            filename=f"{job_id}.txt"
        )
    return {"error": "El archivo aún no está disponible"}
