<!-- eslint-disable vue/valid-v-slot -->
<template>
  <div class="text-center">
    <div class="row">
      <div class="tasks p-4">
        <Layout>
          <template #actions>
            <div class="search-filter">
              <div>
                <Button text="Informacoes" icon="folder" />
                <Input
                  style="width: 35vh; height: 40px"
                  v-model="search"
                  placeholder="Pesquisar"
                />
                <Convert v-model="selectedMeasure" />
                <p>Selecionado: {{ selectedMeasure }}</p>
              </div>

              <div>
                <ExportExcel
                  :data="salesForecast"
                  :columns="salesForecastFields"
                />
                <Button text="Ativar edicao" icon="folder" />
              </div>
            </div>
          </template>
          <template #content>
            <div class="table-container">
              <Table
                :search="search"
                v-if="salesForecast.length > 0"
                :data="salesForecast"
                :columns="salesForecastFields"
                class="table"
                toolbar-text="Informacoes de produtos"
                toolbar-color="#292b2c"
                :sortable="true"
              />

              <Table
                :search="search"
                v-if="salesForecastHistory.length > 0"
                :data="salesForecastHistory"
                :columns="months"
                class="table"
                toolbar-text=""
                toolbar-color="#292b2c"
                :sortable="true"
              />

              <Table
                :search="search"
                v-if="salesForecastForecast.length > 0"
                :data="salesForecastForecast"
                :columns="months"
                class="table"
                toolbar-text=""
                toolbar-color="#292b2c"
                :sortable="true"
              />
            </div>
          </template>
        </Layout>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import Table from "@/components/Table.vue";
import Layout from "@/components/Layout.vue";
import { computed, ref, watch } from "vue";
import { Input } from "@progress/kendo-vue-inputs";
import Button from "@/components/Button.vue";
import ExportExcel from "@/components/ExportExcel.vue";
import { useSalesForecastStore } from "@/stores/salesForecast";
import { DataTableHeader } from "@/types/common";
import Convert from "@/components/Convert.vue";

const search = ref("");

const salesForecastStore = useSalesForecastStore();
salesForecastStore.getSalesForecast();

interface MonthHeader {
  title: string;
  field: string;
}

const months: MonthHeader[] = [
  { title: "Jan", field: "jan" },
  { title: "Feb", field: "feb" },
  { title: "Mar", field: "mar" },
  { title: "Apr", field: "apr" },
  { title: "May", field: "may" },
  { title: "Jun", field: "jun" },
  { title: "Jul", field: "jul" },
  { title: "Aug", field: "aug" },
  { title: "Sep", field: "sep" },
  { title: "Oct", field: "oct" },
  { title: "Nov", field: "nov" },
  { title: "Dec", field: "dec" },
];

const salesForecastFields: DataTableHeader[] = [
  { title: "BO", field: "bo", class: "bg-dark" },
  { title: "Família", field: "family", class: "bg-dark" },
  { title: "Produto", field: "description", class: "bg-dark" },
  { title: "Min. Stock", field: "min_stock", class: "bg-dark" },
  { title: "Stock", field: "stock", class: "bg-dark" },
  { title: "Reservado", field: "min_reserved", class: "bg-dark" },
];
const salesForecast = computed(() => salesForecastStore.data);
const salesForecastHistory = computed(() => salesForecastStore.dataHistory);
const salesForecastForecast = computed(() => salesForecastStore.dataForecast);

const fieldList = salesForecastFields.map(
  (field: DataTableHeader) => field.value
);
type Fields = typeof fieldList;
type SelectedField = {
  [key in Fields[number]]: boolean;
};
const selectedFields = ref<SelectedField>({});
const selectedMeasure = ref();
</script>

<style>
h1 {
  color: #a30526;
}

h3 {
  color: #ffffff;
  font-size: 18px;
}

.btn-information {
  background-color: #a30526 !important;
  color: #ffffff !important;
}

.search-filter {
  display: flex;
  justify-content: space-between;
  gap: 1fr 1fr 1fr;
  margin-bottom: 10px;
}

.search-filter > div > button {
  margin: 0px 6px;
}

.search-filter > div {
  display: flex;
}

.table {
  height: 100% !important;
}

.table-container {
  display: flex;
  overflow-x: auto;
}

.k-grid {
  width: 160vh !important;
}
</style>
