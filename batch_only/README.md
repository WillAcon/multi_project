## 📂 Estructura de Carpetas

Dentro de tu directorio compartido (`shared`), la estructura esperada es la siguiente:

```
shared/
├── input/        # Archivos de entrada subidos por el usuario
├── output/       # Resultados procesados por el worker
└── queue/        # Colas de tareas (JSON) organizadas por tipo
    ├── Foar/
    ├── Noar/
    └── Otro/
```

Ejemplo:  
- Archivos `.txt` y `.xlsx` subidos → van a `input/`  
- Archivos de progreso `.json` generados por el backend → van a `queue/{tipo}/`  
- Archivos finales generados por el worker → se guardan en `output/{tipo}/{job_id}/`

---

## 📂 Carpeta de Prueba

En este repo tienes la carpeta `TEST-FILE/` como ejemplo:  

```
TEST-FILE/
└── input/
    └── Foar/uuid-0100990-123
└── uuid-0100990-123.json   # archivo de progreso que deberías mover a queue/Foar
```

📌 Ese archivo `uuid-0100990-123.json` debe colocarse en la ruta:  

```
shared/queue/Foar/uuid-0100990-123.json
```

para que el **worker** lo lea y lo procese.

---

## ⚙️ Configuración de Rutas en `worker.py`

El proyecto está preparado para funcionar en **Mac/Linux** y **Windows**.  

En `worker.py`  se definen estas rutas:

```python
import os

# Mac / Linux → en Documents/shared
BASE_DIR = os.path.expanduser("~/Documents/shared")

# Windows → en disco D (descomentar si usas otro path)
# BASE_DIR = "D:/shared"

INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
QUEUE_DIR = os.path.join(BASE_DIR, "queue")
```

---

## 🚀 Pasos para Configurar

### 🔹 En **Windows**
1. Crea la carpeta en `D:\shared` con la estructura:
   ```
   D:\shared\input
   D:\shared\output
   D:\shared\queue
   ```
2. En `worker.py` asegúrate de tener:
   ```python
   BASE_DIR = "D:/shared"
   ```

---

## ✅ Pruebas

- Ejecutar python:
  ```
  python3 worker.py
  ```
- Cuando llegue al 100%, los resultados estarán en:
  ```
  shared/output/Foar/{job_id}/
  ```

---
