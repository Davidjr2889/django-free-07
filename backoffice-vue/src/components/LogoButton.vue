<template>
  <div class="w-full h-fit px-8 py-4 max-w-[250px] m-auto">
    <img class="m-auto" :class="{ 'cursor-pointer': clickable }" src="../assets/images/logo-licor-beirao.png"
      :alt="appName" @click="goHome" />
    <small class="text-xs text-white/40">{{ version }}</small>
  </div>
</template>

<script setup lang="ts">
const appName = import.meta.env.VITE_APP_NAME ?? 'App';
const version = import.meta.env.VITE_APP_VERSION ?? '0.0.0';

const props = defineProps({
  clickable: {
    type: Boolean,
    default: true,
  },
});

function goHome () {
  if (!props.clickable) return;
  window.location.href = '/';
}
</script>
