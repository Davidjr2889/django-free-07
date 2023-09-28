<template>
  <div class="tasks p-4">
    <nav aria-label="breadcrumb">
      <ol class="breadcrumb">
        <li class="breadcrumb-item">Previsão Logística</li>
        <li class="breadcrumb-item active" aria-current="page">Sub-Título</li>
      </ol>
    </nav>

    // Criasol
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useMainStore } from "@/stores";

const mainStore = useMainStore();

const isAdminUser = computed(() => {
  return mainStore.isAdminUser;
});

const canDoX = computed(() => {
  return mainStore.userHasPerm("can_X");
});
</script>

<style>
th.k-header.active > div > div {
  color: #fff;
  background-color: #92031c;
}
</style>
