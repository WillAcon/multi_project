import os, time, json,uuid, asyncio
import shutil
import random

BASE_DIR = os.path.expanduser("~/Documents/shared")
# BASE_DIR = "D:/shared" # en caso de utilizar un disco D en windows
 
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
QUEUE_DEPURADOR_DIR = os.path.join(BASE_DIR, "queue_depurador")

# DONE_DIR = os.path.join(BASE_DIR, "done")

print("INPUT_DIR:", INPUT_DIR)
print("OUTPUT_DIR:", OUTPUT_DIR)
print("QUEUE_DEPURADOR_DIR:", QUEUE_DEPURADOR_DIR)

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(QUEUE_DEPURADOR_DIR, exist_ok=True)
# os.makedirs(DONE_DIR, exist_ok=True)

async def process_task(task: str, task_file: str):
    print('ejecutando process_task')

    total_steps = 20
    for i in range(total_steps):
        await asyncio.sleep(0.5)
        percent = int(((i + 1) / total_steps) * 100)
        with open(task_file, "w") as f:
            json.dump({
                "job_id": task,
                "task": task,
                "progress": percent,
                "estado_validacion": 0 if percent < 100 else random.randint(1, 2),
                "status": 2 if percent < 100 else 3
            }, f)
    print(f"Tarea completada: {task} ) ✅")


def main():
    print("👂 Batch worker escuchando en queue depurador...", flush=True)
    while True:
        files = sorted(
            [f for f in os.listdir(QUEUE_DEPURADOR_DIR) if f.endswith(".json")],
            key=lambda f: os.path.getctime(os.path.join(QUEUE_DEPURADOR_DIR, f))
        )
        for file in files:
            task = os.path.splitext(file)[0]  # nombre del task (sin extensión)
            task_file = os.path.join(QUEUE_DEPURADOR_DIR, file)

            try:
                with open(task_file) as f:
                    data = json.load(f)
            except (json.JSONDecodeError, OSError):
                # archivo vacío o aún escribiéndose → esperar al siguiente ciclo
                continue

            progress = data.get("progress", 0)

            # 🚫 Archivos completados (progress=100)
            if progress >= 100:
                # Si lleva más de 10 segundos, lo limpiamos
                age = time.time() - os.path.getctime(task_file)
                if age > 10:
                    print(f"🧹 Limpiando tarea {task} con progress=100 que no fue borrada en 10s")
                    os.remove(task_file)
                continue  # no reprocesar

            # ✅ Solo procesar tareas pendientes
            print(f"🔎 Nueva tarea detectada -> task={task}", flush=True)
            print(f"Procesando tarea {task}...", flush=True)
            asyncio.run(process_task(task, task_file))
            print(f"✅ Tarea {task} finalizada", flush=True)

        time.sleep(2)




if __name__ == "__main__":
    main()




