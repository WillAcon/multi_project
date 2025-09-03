from fastapi import FastAPI, UploadFile, File
from fastapi_sse import sse_handler
from pydantic import BaseModel
import os, uuid, json, asyncio
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


INPUT_DIR = "/srv/shared/input"
PROGRESS_DIR = "/srv/shared/progress"
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(PROGRESS_DIR, exist_ok=True)

 
class ProgressMsg(BaseModel):
    progress: int


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())
    input_file = os.path.join(INPUT_DIR, f"{job_id}.txt")

    # Guardar archivo subido
    with open(input_file, "wb") as f:
        f.write(await file.read())

    # Crear archivo de progreso inicial
    progress_file = os.path.join(PROGRESS_DIR, f"{job_id}.json")
    with open(progress_file, "w") as f:
        json.dump({"progress": 0}, f)

    return {"job_id": job_id}


@app.get("/events/{job_id}")
@sse_handler()  # 👈 fastapi-sse convierte el yield en un stream SSE
async def sse_events(job_id: str):
    progress_file = os.path.join(PROGRESS_DIR, f"{job_id}.json")
    last_progress = -1
    while True:
        if os.path.exists(progress_file):
            with open(progress_file) as f:
                data = json.load(f)

            if data["progress"] != last_progress:
                last_progress = data["progress"]
                yield ProgressMsg(progress=last_progress)

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
