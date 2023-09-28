<template>
  <Button :icon="props.icon" style="height: 40px">{{ props.text }}</Button>
</template>

<script setup lang="ts">
import { defineProps } from "vue";
import { Button } from "@progress/kendo-vue-buttons";

const props = defineProps(["text", "icon", "click"]);
</script>
