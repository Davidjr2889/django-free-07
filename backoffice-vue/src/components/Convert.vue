<template>
  <div class="dropdown">
    <kendo-dropdownlist
      class="dropdownlist"
      :data-items="measureUnits"
      v-model="selectedItem"
      @change="updateSelectedItem"
      :text-field="'text'"
      :value-field="'value'"
      :default-item="{ text: 'Converter em', value: null }"
    ></kendo-dropdownlist>
  </div>
</template>

<script>
import { ref, watch } from "vue";
import { DropDownList } from "@progress/kendo-vue-dropdowns";

export default {
  components: {
    kendoDropdownlist: DropDownList,
  },
  props: {
    value: String,
  },
  setup(props, ctx) {
    const selectedItem = ref(props.value || null);

    watch(selectedItem, (newVal) => {
      ctx.emit("update:value", newVal);
    });

    const updateSelectedItem = (e) => {
      selectedItem.value = e;
    };

    const measureUnits = [
      { text: "Unidades", value: "unities" },
      { text: "Caixas", value: "boxes" },
      { text: "Caixas de 9l", value: "boxes-9l" },
    ];

    return {
      selectedItem,
      updateSelectedItem,
      measureUnits,
    };
  },
};
</script>

<style scoped>
.dropdown {
  display: grid;
}
</style>
