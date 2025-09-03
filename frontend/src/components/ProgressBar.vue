<template>
  <div class="hidden " style="margin-top:20px; width:300px; border:1px solid #ccc; border-radius:4px;">
    <div
      :style="{
        width: progress + '%',
        background: '#42b883',
        height: '20px',
        transition: 'width 0.5s'
      }"
    ></div>
  </div>
  <p class="hidden">{{ progress }}%</p>

<div class="my-4"></div>

 <div
    class="radial-progress bg-accent text-accent-content border-accent border-4"
    :style="{ '--value': progress }"
    :aria-valuenow="progress"
    role="progressbar"
  >
    {{ progress }}%
  </div>


</template>

<script setup>
defineProps({
  progress: {
    type: Number,
    default: 0
  }
})
</script>
