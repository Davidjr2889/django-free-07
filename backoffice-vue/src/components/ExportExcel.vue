<template>
  <Button text="Exportar relatorio" :click="exportToExcel" />
</template>

<script setup lang="ts">
import { defineProps } from "vue";
import Button from "./Button.vue";
import { saveExcel } from "@progress/kendo-vue-excel-export";

const props = defineProps(["data", "columns"]);

const exportToExcel = () => {
  saveExcel({
    data: props.data,
    columns: props.columns,
    fileName: "arquivo",
  });
};
</script>
