from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
import os, uuid, json, asyncio
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi_sse import sse_handler
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


INPUT_DIR = "/srv/shared/input"
OUTPUT_DIR = "/srv/shared/output"
QUEUE_DIR = "/srv/shared/queue"

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(QUEUE_DIR, exist_ok=True)


 
class ProgressMsg(BaseModel):
    progress: int
    task: str
    job_id: str
    status: Optional[int] = None


@app.post("/upload")
async def upload_file(
    tipo: str = Form(...), 
    txt_file: UploadFile = File(...), 
    excel_file: UploadFile = File(...)
):
    job_id = str(uuid.uuid4())
    task_dir = os.path.join(INPUT_DIR, tipo, job_id)
    os.makedirs(task_dir, exist_ok=True)
    # Guardar archivo TXT como base.txt
    txt_path = os.path.join(task_dir, "base.txt")
    with open(txt_path, "wb") as f:
        f.write(await txt_file.read())
    # Guardar archivo Excel como diccionario.xlsx
    excel_path = os.path.join(task_dir, "diccionario.xlsx")
    with open(excel_path, "wb") as f:
        f.write(await excel_file.read())
    return {"job_id": job_id, "tipo": tipo, "message": "Archivos guardados correctamente"}

@app.post("/start/queue")
async def start_queue(job_id: str = Form(...), tipo: str = Form(...)):
    task_dir = os.path.join(QUEUE_DIR, tipo)
    os.makedirs(task_dir, exist_ok=True)

    progress_file = os.path.join(task_dir, f"{job_id}.json")
    with open(progress_file, "w") as f:
        json.dump({"progress": 0}, f)

    return {"job_id": job_id, "tipo": tipo, "message": "Cola iniciada"}

@app.get("/events/{tipo}/{job_id}")
@sse_handler()  # fastapi-sse convierte el yield en un stream SSE
async def sse_events(tipo: str, job_id: str):
    progress_file = os.path.join(QUEUE_DIR, tipo, f"{job_id}.json")
    last_progress = -1

    while True:
        if os.path.exists(progress_file):
            with open(progress_file) as f:
                data = json.load(f)

            progress = data.get("progress", 0)

            if progress != last_progress:
                last_progress = progress
                yield ProgressMsg(
                    progress=progress,
                    tipo=tipo,
                    job_id=job_id,
                    status="completo" if progress >= 100 else "en_progreso"
                )

            if last_progress >= 100:
                break

        await asyncio.sleep(1)


# ✅ Descargar resultado
@app.get("/result/{job_id}")
async def download_result(job_id: str):
    output_file = os.path.join(OUTPUT_DIR, f"{job_id}.txt")
    if os.path.exists(output_file):
        return FileResponse(output_file, filename=f"{job_id}.txt")
    return {"error": "Resultado aún no disponible"}
