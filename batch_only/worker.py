import os, time, json,uuid, asyncio
import shutil
import random

BASE_DIR = os.path.expanduser("~/Documents/shared")
# BASE_DIR = "D:/shared" # en caso de utilizar un disco D en windows
 
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
QUEUE_DIR = os.path.join(BASE_DIR, "queue")
# DONE_DIR = os.path.join(BASE_DIR, "done")

print("INPUT_DIR:", INPUT_DIR)
print("OUTPUT_DIR:", OUTPUT_DIR)
print("QUEUE_DIR:", QUEUE_DIR)

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(QUEUE_DIR, exist_ok=True)
# os.makedirs(DONE_DIR, exist_ok=True)

async def process_task(seccion: str, task: str, task_file: str):
    print('ejecutando process_task')
    input_dir = os.path.join(INPUT_DIR, seccion, task)
    output_dir = os.path.join(OUTPUT_DIR, seccion, task)
    os.makedirs(output_dir, exist_ok=True)

    total_steps = 20
    for i in range(total_steps):
        await asyncio.sleep(0.5)
        percent = int(((i + 1) / total_steps) * 100)
        with open(task_file, "w") as f:
            reporte_csv = '218371296321874623874628376487235487235 copia 2'
            json.dump({
                "seccion": seccion, # app_bd o app_bd2
                "job_id": task,
                "task": task,
                "progress": percent,
                "estado_validacion": 0 if percent < 100 else random.randint(1, 2),
                "status": 2 if percent < 100 else 3,
                "reporte_csv": reporte_csv
            }, f)
    print(f"Tarea completada: {task} (seccion={seccion}) ✅")

def main():
    print("Batch worker escuchando en queue...", flush=True)
    while True:
        for seccion in os.listdir(QUEUE_DIR):
            seccion_path = os.path.join(QUEUE_DIR, seccion)
            if not os.path.isdir(seccion_path):
                continue
            # ordenar por fecha de creación
            files = sorted(
                os.listdir(seccion_path),
                key=lambda f: os.path.getctime(os.path.join(seccion_path, f))
            )

            for file in files:
                if not file.endswith(".json"):
                    continue

                task = os.path.splitext(file)[0]  # nombre del task (job_id)
                task_file = os.path.join(seccion_path, file)

                try:
                    with open(task_file) as f:
                        data = json.load(f)
                except (json.JSONDecodeError, OSError):
                    # archivo vacío o en proceso de escritura, esperar al próximo ciclo
                    continue
                progress = data.get("progress", 0)
                # 🚫 Archivos completados (progress=100)
                if progress >= 100:
                    # Si lleva más de 10 segundos, lo limpiamos
                    age = time.time() - os.path.getctime(task_file)
                    if age > 10:
                        print(f"🧹 Limpiando tarea {task} (seccion={seccion}) con progress=100 que no fue borrada en 10s")
                        os.remove(task_file)
                    continue  # no reprocesar
                # ✅ Solo procesar tareas pendientes
                print(f"🔎 Nueva tarea detectada -> seccion={seccion}, task={task}", flush=True)
                print(f"Procesando tarea {task} (seccion={seccion})...", flush=True)
                asyncio.run(process_task(seccion, task, task_file))
                print(f"✅ Tarea {task} (seccion={seccion}) finalizada", flush=True)

        time.sleep(2)



if __name__ == "__main__":
    main()




