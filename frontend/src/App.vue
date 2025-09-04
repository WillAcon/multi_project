<template>
  <div style="padding:20px;">
    <h1 class="font-bold my-4">Monitor de Progreso</h1>

    <!-- Selección de tipo -->
    <div class="my-2">
      <label class="font-semibold">Tipo:</label>
      <select v-model="tipo" class="select select-bordered w-full max-w-xs">
        <option disabled value="">Seleccione un tipo</option>
        <option value="Foar">Foar</option>
        <option value="Noar">Noar</option>
        <option value="Otro">Otro</option>
      </select>
    </div>

    <!-- Subida de archivo TXT -->
    <div class="my-2">
      <label class="font-semibold">Archivo TXT:</label>
      <input 
        type="file" 
        accept=".txt" 
        @change="onTxtChange"
        class="file-input file-input-bordered w-full max-w-xs"
      />
    </div>

    <!-- Subida de archivo Excel -->
    <div class="my-2">
      <label class="font-semibold">Archivo Excel:</label>
      <input 
        type="file" 
        accept=".xlsx,.xls" 
        @change="onExcelChange"
        class="file-input file-input-bordered w-full max-w-xs"
      />
    </div>

    <button 
      :disabled="!txtFile || !excelFile || !tipo" 
      @click="uploadFiles" 
      class="btn btn-primary mt-2"
    >
      Subir Archivos
    </button>

    <!-- Lista de tareas -->
    <div v-if="tasks.length > 0" class="mt-6">
      <h2 class="font-bold mb-2">Tareas Pendientes</h2>
      <ul class="space-y-2">
        <li v-for="task in tasks" :key="task.id" class="flex items-center justify-between border p-2 rounded">
          <span>ID: {{ task.id }} ({{ task.tipo }})</span>
          <button class="btn btn-sm btn-accent" @click="startTask(task.id,task.tipo)">
            ▶️ Iniciar
          </button>
        </li>
      </ul>
    </div>

    <!-- Barra de progreso --> 
    <div v-if="progress > 0">
      <ProgressBar :progress="progress" />
    </div>

    <!-- Botón de descarga visible solo cuando termina -->
    <div v-if="progress >= 100" class="mt-4">
      <button @click="downloadResult" class="btn btn-success">
        Descargar Resultado
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onBeforeUnmount } from "vue"
import ProgressBar from "./components/ProgressBar.vue"
import api from "./services/api"

const txtFile = ref(null)
const excelFile = ref(null)
const tipo = ref("")
const tasks = ref([])   // lista de tareas creadas
const progress = ref(0)
let currentTaskId = null
let eventSource = null

function onTxtChange(e) {
  txtFile.value = e.target.files[0] || null
}

function onExcelChange(e) {
  excelFile.value = e.target.files[0] || null
}

async function uploadFiles() {
  if (!txtFile.value || !excelFile.value || !tipo.value) {
    alert("Selecciona el tipo y ambos archivos")
    return
  }

  const formData = new FormData()
  formData.append("tipo", tipo.value)
  formData.append("txt_file", txtFile.value)
  formData.append("excel_file", excelFile.value)

  // 🚀 Subir ambos archivos al backend
  const res = await api.post("/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  })

  const newTaskId = res.data.job_id
  tasks.value.push({ id: newTaskId, tipo: tipo.value })
  txtFile.value = null
  excelFile.value = null
  tipo.value = ""
}

async function startTask(taskId, tipo) {
    console.log("startTask", taskId);
    console.log("startTask", tipo);

  const task = tasks.value.find(t => t.id === taskId)
  if (!task) return


  const formData = new FormData()
  formData.append("job_id", task.id)
  formData.append("tipo", task.tipo)

    // 🚀 Enviar al backend
  await api.post("/start/queue", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  })

  currentTaskId = taskId

  // 🔗 Conectarse al SSE
  eventSource = new EventSource(`${api.defaults.baseURL}/events/${tipo}/${taskId}`)

  eventSource.addEventListener("message", (e) => {

    try {
      const payload = JSON.parse(e.data)
        console.log("payload", payload)

      if (payload.progress !== undefined) {
        progress.value = payload.progress
        console.log("Progreso recibido:", progress.value)

        if (progress.value >= 100) {
          console.log("Proceso finalizado ✅")
          eventSource.close()
        }
      }
    } catch (err) {
      console.error("Error parseando SSE:", err, e.data)
    }
  })

  eventSource.onerror = (err) => {
    console.error("SSE error:", err)
    eventSource.close()
  }
}

onBeforeUnmount(() => {
  if (eventSource) eventSource.close()
})
</script>
