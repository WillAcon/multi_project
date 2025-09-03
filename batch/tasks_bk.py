import redis, time, os, random

# aqui está la función para procesar la data
def process_job(input_param: str, job_id: str):
    r = redis.Redis(
        host=os.getenv("REDIS_HOST", "redis"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        db=0
    )
    output_dir = "/batch/output"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{input_param}_{job_id}.txt")
    total = 20
    with open(output_file, "w") as f:
        for i in range(total):
            time.sleep(1)
            number = random.randint(1, 1000)
            f.write(f"{number}\n")
            f.flush()
            percent = int(((i + 1) / total) * 100)
            r.set(f"progress:{job_id}", percent)
            print(f"[{job_id}] Procesado {percent}%")

    r.set(f"progress:{job_id}", 100)
    print(f"[{job_id}] Finalizado -> {output_file}")
