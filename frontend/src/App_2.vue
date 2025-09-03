<template>
  <div style="padding:20px;">
    <h1 class="font-bold my-4">Monitor de Progreso</h1>

    <!-- Campo para escribir el nombre del archivo -->
    <input
      v-model="fileName"
      required
      type="text"
      :disabled="(progress > 0 && progress < 100) || (progress==0 && taskId)"
      placeholder="Nombre del archivo"
      class="input input-bordered w-full max-w-xs"
    />

    <button :disabled="(progress > 0 && progress < 100) || (progress==0 && taskId)" @click="startBatch" class="btn btn-primary ml-2">Iniciar Proceso</button>

    <ProgressBar :progress="progress" />

    <div v-if="taskId" class="my-4">
      <span class="font-bold">ID Tarea:</span> <br>
      {{ taskId }}
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"
import ProgressBar from "./components/ProgressBar.vue"
import api from "./services/api"

const progress = ref(0)
const taskId = ref(null)
const fileName = ref("")  // 🔹 archivo dinámico
let interval = null

async function startBatch() {
  if (!fileName.value) {
    alert("Por favor ingresa un nombre de archivo")
    return
  }

  // Puedes enviarlo como query param:
  const res = await api.post(`/start?input_param=${fileName.value}`)
  // O como body (si tu backend acepta JSON):
  // const res = await api.post("/start", { input_param: fileName.value })
  console.log("res startBatch", res)
  taskId.value = res.data.job_id
  progress.value = 0

  if (interval) clearInterval(interval)
  interval = setInterval(checkProgress, 2000)
}

async function checkProgress() {
  if (!taskId.value) return
  const res = await api.get(`/progress/${taskId.value}`)
  console.log("res progress", res)

  progress.value = res.data.progress
  if (progress.value >= 100) clearInterval(interval)
}
</script>
