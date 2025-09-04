import os, time, json, asyncio
import shutil

BASE_DIR = os.path.expanduser("~/Documents/shared")
# BASE_DIR = "D:/shared" # en caso de utilizar un disco D en windows

INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
QUEUE_DIR = os.path.join(BASE_DIR, "queue")

print("INPUT_DIR:", INPUT_DIR)
print("OUTPUT_DIR:", OUTPUT_DIR)
print("QUEUE_DIR:", QUEUE_DIR)

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(QUEUE_DIR, exist_ok=True)

async def process_task(tipo: str, job_id: str, task_file: str):
    input_dir = os.path.join(INPUT_DIR, tipo, job_id)
    output_dir = os.path.join(OUTPUT_DIR, tipo, job_id)
    os.makedirs(output_dir, exist_ok=True)

    base_file = os.path.join(input_dir, "base.txt")
    diccionario_file = os.path.join(input_dir, "diccionario.xlsx")

    base_result = os.path.join(output_dir, "base_result.txt")
    diccionario_result = os.path.join(output_dir, "diccionario_result.xlsx")

    total_steps = 10
    for i in range(total_steps):
        time.sleep(0.5)  # 🔹 Simula trabajo pesado
        percent = int(((i + 1) / total_steps) * 100)

        # 🔹 Actualizar progreso en la cola
        with open(task_file, "w") as f:
            json.dump({
                "job_id": job_id,
                "tipo": tipo,
                "progress": percent
            }, f)

    # ✅ Simular resultados al completar el proceso
    # base_result.txt = base.txt con sufijo "-procesado"
    if os.path.exists(base_file):
        with open(base_file, "r") as f_in, open(base_result, "w") as f_out:
            for line in f_in:
                f_out.write(line.strip() + " - procesado\n")

    # diccionario_result.xls = copia simulada del diccionario
    if os.path.exists(diccionario_file):
        shutil.copy(diccionario_file, diccionario_result)

    # 🔹 Guardar estado final en la cola
    with open(task_file, "w") as f:
        json.dump({
            "job_id": job_id,
            "tipo": tipo,
            "progress": 100,
            "status": "completo"
        }, f)

    print(f"Tarea completada: {job_id} ({tipo}) ✅")

def main():
    print("Batch worker escuchando en queue...", flush=True)
    while True:
        for tipo in os.listdir(QUEUE_DIR):
            tipo_path = os.path.join(QUEUE_DIR, tipo)
            if not os.path.isdir(tipo_path):
                continue

            for file in os.listdir(tipo_path):
                if file.endswith(".json"):
                    job_id = os.path.splitext(file)[0]
                    task_file = os.path.join(tipo_path, file)

                    with open(task_file) as f:
                        data = json.load(f)

                    if data.get("progress", 0) < 100:
                        print(f"🔎 Nueva tarea detectada -> job_id={job_id}, tipo={tipo}", flush=True)
                        print(f"Procesando tarea {job_id} ({tipo})...", flush=True)

                        asyncio.run(process_task(tipo, job_id, task_file))

                        print(f"✅ Tarea {job_id} ({tipo}) completada y eliminada de la cola.", flush=True)
                        os.remove(task_file)

        time.sleep(2)

if __name__ == "__main__":
    main()

