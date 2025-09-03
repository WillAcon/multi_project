import os, time, json

BASE_DIR = "/srv/shared"
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
PROGRESS_DIR = os.path.join(BASE_DIR, "progress")

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PROGRESS_DIR, exist_ok=True)


def process_file(job_id: str):
    input_file = os.path.join(INPUT_DIR, f"{job_id}.txt")
    output_file = os.path.join(OUTPUT_DIR, f"{job_id}.txt")
    progress_file = os.path.join(PROGRESS_DIR, f"{job_id}.json")

    with open(input_file, "r") as fin, open(output_file, "w") as fout:
        lines = fin.readlines()
        total = len(lines)

        for i, line in enumerate(lines, start=1):
            num = int(line.strip())
            fout.write(f"{num * 2}\n")
            fout.flush()

            # Simular procesamiento pesado
            time.sleep(0.5)

            # Guardar progreso
            percent = int((i / total) * 100)
            with open(progress_file, "w") as f:
                json.dump({"progress": percent}, f)

    print(f"[{job_id}] Procesamiento completado")


if __name__ == "__main__":
    print("Batch worker iniciado...")
    while True:
        for file in os.listdir(INPUT_DIR):
            job_id, ext = os.path.splitext(file)
            if ext == ".txt":
                progress_file = os.path.join(PROGRESS_DIR, f"{job_id}.json")
                if os.path.exists(progress_file):
                    with open(progress_file) as f:
                        state = json.load(f)
                    if state["progress"] < 100:
                        process_file(job_id)
        time.sleep(5)
