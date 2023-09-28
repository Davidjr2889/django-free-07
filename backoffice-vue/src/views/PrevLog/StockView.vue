<template>
  <div class="container text-center">
    <h1 class="text-start pb-4 px-2">Estoque</h1>

    <div class="row">
      <div class="col-2">
        <Menu :items="menuItems">
          <template v-slot:item="menuItem">
            <Button @click="menuItem.itemClick">
              <kendo-icon :name="menuItem.icon"></kendo-icon>
              {{ menuItem.text }}
              <kendo-icon :name="menuItem.arrowIcon"></kendo-icon>
            </Button>
          </template>
        </Menu>
      </div>

      <div class="col-4">
        <Input
          v-model="search"
          placeholder="Digite um produto, família ou BO"
        ></Input>
      </div>

      <div class="col-2">
        <Menu :items="measureUnits" :select="onMeasureUnitSelect">
          <template v-slot:item="menuItem">
            <MenuItem>
              {{ menuItem.text }}
            </MenuItem>
          </template>
        </Menu>
      </div>

      <div class="col-2"></div>

      <div class="col-2">
        <Button
          :loading="isExportLoading"
          :disabled="isExportLoading"
          @click="exportToExcel"
          :style="{
            'max-width': 'inherit',
            'font-size': '0.7rem',
            height: '45px',
            'margin-top': '-5px',
            color: 'darkgreen',
          }"
        >
          <kendo-icon :name="'file-excel'"></kendo-icon>
          Exportar
        </Button>
      </div>
    </div>

    <div class="row">
      <div class="col-12">
        <Grid
          :data-items="stockProducts"
          :columns="stockProductsColumns"
          :groupable="true"
          :height="'70vh'"
        ></Grid>
      </div>
    </div>

    <div class="row">
      <div class="col-6 text-start justify-content-start">
        <Button
          @click="$router.push('/change_log')"
          :color="'#A30526'"
          :style="{ padding: '0', color: '#A30526' }"
        >
          <kendo-icon :name="'clock-outline'" :position="'left'"></kendo-icon>
          Log de alterações
        </Button>
      </div>

      <div class="col-6"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useStockStore } from "@/stores/stock";
import { Button } from "@progress/kendo-vue-buttons";
import { Input } from "@progress/kendo-vue-inputs";
import { Menu, MenuItem } from "@progress/kendo-vue-layout";
import { Grid } from "@progress/kendo-vue-grid";

const search = ref("");

const stockStore = useStockStore();
stockStore.getStockProducts();

const stockProductsColumns = [
  { field: "bo", title: "BO", headerClassName: "bg-dark" },
  { field: "family", title: "Família", headerClassName: "bg-dark" },
  { field: "description", title: "Produto", headerClassName: "bg-dark" },
  { field: "article", title: "SKU", headerClassName: "bg-dark" },
  { field: "min_stock", title: "Min. Stock", headerClassName: "bg-dark" },
  { field: "stock", title: "Stock", headerClassName: "bg-dark" },
  { field: "min_reserved", title: "Reservado", headerClassName: "bg-dark" },
];
const stockProducts = computed(() => stockStore.data);

const fieldList = stockProductsColumns.map(
  (column: GridColumn) => column.field
);
type Fields = typeof fieldList;
type SelectedField = {
  [key in Fields[number]]: boolean;
};
const selectedFields = ref<SelectedField>({});

const measureUnits = [
  { text: "Unidades", value: "unities" },
  { text: "Caixas", value: "boxes" },
  { text: "Caixasde 9l", value: "boxes-9l" },
];
const selectedMeasure = ref(measureUnits[0]);

const isExportLoading = ref(false);
const exportToExcel = () => {
  isExportLoading.value = true;
  setTimeout(() => {
    isExportLoading.value = false;
  }, 2000);
};

const menuItems = [
  {
    text: "Informações",
    icon: "cog",
    arrowIcon: "chevron-down",
    itemClick() {},
  },
];

const onMeasureUnitSelect = (e) => {
  selectedMeasure.value = e.itemData;
};
</script>

<style scoped>
h1 {
  color: #a30526;
}

h3 {
  color: #ffffff;
  font-size: 18px;
}
</style>
