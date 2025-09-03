from fastapi import FastAPI, UploadFile, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import os, uuid, json, asyncio

BASE_DIR = "/srv/shared"
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
PROGRESS_DIR = os.path.join(BASE_DIR, "progress")

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PROGRESS_DIR, exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ✅ Subida de archivo
@app.post("/upload")
async def upload_file(file: UploadFile):
    job_id = str(uuid.uuid4())
    input_path = os.path.join(INPUT_DIR, f"{job_id}.txt")
    progress_path = os.path.join(PROGRESS_DIR, f"{job_id}.json")

    # Guardar archivo en shared_files/input
    with open(input_path, "wb") as f:
        f.write(await file.read())

    # Crear progreso inicial
    with open(progress_path, "w") as f:
        json.dump({"progress": 0}, f)

    return {"job_id": job_id}

@app.get("/events/{job_id}")
async def sse_progress(job_id: str):
    progress_file = os.path.join(PROGRESS_DIR, f"{job_id}.json")

    async def event_generator():
        last_progress = -1
        while True:
            if os.path.exists(progress_file):
                with open(progress_file) as f:
                    data = json.load(f)

                if data["progress"] != last_progress:
                    last_progress = data["progress"]
                    yield {
                        "event": "progress",
                        "data": str(last_progress)
                    }

                # ✅ cuando llegue al 100 mandamos un último evento y salimos
                if last_progress >= 100:
                    yield {"event": "done", "data": "completed"}
                    return   # 👈 en lugar de break

            await asyncio.sleep(1)

    return EventSourceResponse(event_generator())

# ✅ Descargar resultado
@app.get("/result/{job_id}")
async def download_result(job_id: str):
    output_file = os.path.join(OUTPUT_DIR, f"{job_id}.txt")
    if os.path.exists(output_file):
        return FileResponse(output_file, filename=f"{job_id}.txt")
    return {"error": "Resultado aún no disponible"}
