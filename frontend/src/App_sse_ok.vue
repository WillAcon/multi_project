<template>
  <div style="padding:20px;">
    <h1 class="font-bold my-4">Monitor de Progreso</h1>

    <!-- Subida de archivo -->
    <input 
      type="file" 
      accept=".txt" 
      @change="onFileChange"
      class="file-input file-input-bordered w-full max-w-xs"
    />

    <button 
      :disabled="!selectedFile || (progress > 0 && progress < 100)" 
      @click="uploadFile" 
      class="btn btn-primary ml-2"
    >
      Subir y Procesar
    </button>

    <ProgressBar :progress="progress" />

    <div v-if="taskId" class="my-4">
      <span class="font-bold">ID Tarea:</span> <br>
      {{ taskId }}
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

const progress = ref(0)
const taskId = ref(null)
const selectedFile = ref(null)
let eventSource = null  // 🔹 conexión SSE

function onFileChange(event) {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
  }
}

async function uploadFile() {
  if (!selectedFile.value) {
    alert("Por favor selecciona un archivo .txt")
    return
  }

  const formData = new FormData()
  formData.append("file", selectedFile.value)

  // 🚀 Subir archivo al backend
  const res = await api.post("/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  })

  taskId.value = res.data.job_id
  progress.value = 0

  // 🔗 Abrir conexión SSE para recibir progreso
  if (eventSource) {
    eventSource.close()
  }

  eventSource = new EventSource(`${api.defaults.baseURL}/events/${taskId.value}`)

eventSource.addEventListener("message", (e) => {
  try {
    const payload = JSON.parse(e.data)   // 👈 convertir string a objeto
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

async function downloadResult() {
  if (!taskId.value) return

  const res = await api.get(`/result/${taskId.value}`, {
    responseType: "blob", // 🔹 importante para descargar archivo
  })

  const url = window.URL.createObjectURL(new Blob([res.data]))
  const link = document.createElement("a")
  link.href = url
  link.setAttribute("download", `${taskId.value}.txt`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// 🧹 Cerrar SSE al salir de la vista
onBeforeUnmount(() => {
  if (eventSource) {
    eventSource.close()
  }
})
</script>
