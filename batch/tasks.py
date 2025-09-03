import os, time, json, asyncio

INPUT_DIR = "/srv/shared/input"
OUTPUT_DIR = "/srv/shared/output"
PROGRESS_DIR = "/srv/shared/progress"

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PROGRESS_DIR, exist_ok=True)


async def process_file(job_id: str, input_file: str):
    with open(input_file, "r") as f:
        lines = f.readlines()

    total = len(lines)
    output_file = os.path.join(OUTPUT_DIR, f"{job_id}.txt")

    with open(output_file, "w") as out:
        for i, line in enumerate(lines):
            time.sleep(0.5)  # simula trabajo pesado
            try:
                num = int(line.strip()) * 2
                out.write(f"{num}\n")
            except ValueError:
                # Ignora líneas no numéricas
                out.write("ERROR\n")
            out.flush()
            # Guardar progreso en archivo JSON
            percent = int(((i + 1) / total) * 100)
            progress_file = os.path.join(PROGRESS_DIR, f"{job_id}.json")
            with open(progress_file, "w") as pf:
                json.dump({"progress": percent}, pf)

def main():
    print("Batch worker escuchando en input...")
    while True:
        for file in os.listdir(INPUT_DIR):
            if file.endswith(".txt"):
                job_id = os.path.splitext(file)[0]
                input_file = os.path.join(INPUT_DIR, file)

                # Procesar archivo (bloqueante pero OK para batch)
                asyncio.run(process_file(job_id, input_file))

                # Opcional: limpiar input
                os.remove(input_file)

        time.sleep(2)


if __name__ == "__main__":
    main()
