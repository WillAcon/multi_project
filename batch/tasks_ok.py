import redis, time, os, random

# nombre de tarea
def process_job(filename: str, job_id: str):
    r = redis.Redis(
        host=os.getenv("REDIS_HOST", "redis"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        db=0
    )
    INPUT_DIR = "/srv/shared/input"
    OUTPUT_DIR = "/srv/shared/output"

    input_file = os.path.join(INPUT_DIR, filename)
    output_file = os.path.join(OUTPUT_DIR, f"{job_id}.txt")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(input_file, "r") as fin, open(output_file, "w") as fout:
        lines = fin.readlines()
        total = len(lines)

        for i, line in enumerate(lines):
            time.sleep(1)  # esto: para simular tiempo de procesamiento
            try:
                number = int(line.strip())
                result = number * 2
            except ValueError:
                result = line.strip()

            fout.write(f"{result}\n")
            fout.flush()

            percent = int(((i + 1) / total) * 100)
            r.set(f"progress:{job_id}", percent)
            print(f"[{job_id}] Procesado {percent}%")

    r.set(f"progress:{job_id}", 100)
    print(f"[{job_id}] Finalizado -> {output_file}")

def process_job_1(filename: str, job_id: str):
    return True
