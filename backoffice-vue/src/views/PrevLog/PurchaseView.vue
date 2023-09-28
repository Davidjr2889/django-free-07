<!-- eslint-disable vue/valid-v-slot -->
<template>
  <div class="container text-center">
    <h1 class="text-start pb-4 px-2">Compras</h1>

    <div class="row">
      <!-- d-flex flex-nowrap justify-content-between flex-row align-items-start -->
      <div class="col-2">
        <v-menu offset-y transition="slide-y-transition" bottom :close-on-content-click="false">
          <template v-slot:activator="{ on }">
            <v-btn v-on="on" class="btn-information"
              style="max-width:inherit;font-size:0.7rem;height: 45px;margin-top: -5px;">
              <v-icon small class="me-1">
                mdi-cog
              </v-icon>
              Informações
              <v-icon small class="ms-1">
                mdi-chevron-down
              </v-icon>
            </v-btn>
          </template>
          <v-list>
            <v-container fluid class="m-0 py-2 d-flex flex-wrap gap-2">
              <v-checkbox class="m-0 p-0" v-model="selectedFields[field.value]" :label="field.text" hide-details dense
                color="primary" v-for="(field, index) in purchaseFields" :key="index">
              </v-checkbox>
            </v-container>
          </v-list>
        </v-menu>
      </div>

      <div class="col-4">
        <v-text-field v-model="search" prepend-inner-icon="mdi-magnify" placeholder="Digite um produto, família ou BO"
          outlined dense></v-text-field>
      </div>

      <div class="col-2">
        <v-menu offset-y transition="slide-y-transition" bottom :close-on-content-click="true">
          <template v-slot:activator="{ on }">
            <v-btn v-on="on" class="btn-information"
              style="max-width:inherit;font-size:0.7rem;height: 45px;margin-top: -5px;">
              <v-icon small class="me-1">
                mdi-vector-arrange-above
              </v-icon>
              Converter em
              <v-icon small class="ms-1">
                mdi-chevron-down
              </v-icon>
            </v-btn>
          </template>
          <v-list>
            <v-list-item link v-for="(measure, index) in measureUnits" :key="index" @click="selectedMeasure = measure">
              <v-list-item-title>{{ measure.text }}</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
      </div>

      <div class="col-2"></div>

      <div class="col-2">
        <v-btn :loading="isExportLoading" :disabled="isExportLoading"
          style="max-width:inherit;font-size:0.7rem;height: 45px;margin-top: -5px;color:darkgreen;" class="" outlined
          @click="exportToExcel">
          <v-icon small class="me-1">
            mdi-file-excel-outline
          </v-icon>
          Exportar
        </v-btn>
      </div>
    </div>

    <div class="row">
      <div class="col-12">
        <v-card class="overflow-hidden">
          <v-card-title class="bg-dark justify-content-center">Informações dos produtos</v-card-title>
          <v-data-table class="elevation-1 overflow-x-auto" dense :headers="purchaseFields" :items="purchases"
            item-key="id" fixed-header height="70vh" group-by="family" :items-per-page="50">
            <template v-slot:group.header="{ items, isOpen, toggle }">
              <th :colspan="purchaseFields.length" class="text-start">
                {{ items[0].family }}
                <v-icon small @click="toggle">{{ isOpen ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
              </th>
            </template>
          </v-data-table>
        </v-card>
      </div>
    </div>

    <div class="row">
      <div class="col-6 text-start justify-content-start">
        <v-btn text color="#A30526" class="p-0" @click="$router.push('/change_log')">
          <v-icon left>mdi-clock-outline</v-icon>
          Log de alterações
        </v-btn>
      </div>

      <div class="col-6"></div>
    </div>
  </div>
</template>


<script setup lang="ts">
import { computed, ref } from 'vue';
import { usePurchaseStore } from '@/stores/purchase';
import { DataTableHeader } from '@/types/common';

const search = ref('');

const purchaseStore = usePurchaseStore();
purchaseStore.getPurchases();
// purchaseStore.putPurchase();
// purchaseStore.postPurchase();

const purchaseFields: DataTableHeader[] = [
  { text: 'BO', value: 'bo', class: 'bg-dark' },
  { text: 'Família', value: 'family', class: 'bg-dark' },
  { text: 'Produto', value: 'description', class: 'bg-dark' },
  { text: 'Min. Stock', value: 'min_stock', class: 'bg-dark' },
  { text: 'Stock', value: 'stock', class: 'bg-dark' },
  { text: 'Reservado', value: 'min_reserved', class: 'bg-dark' },
];
const purchases = computed(() => purchaseStore.data);

const fieldList = purchaseFields.map((field: DataTableHeader) => field.value);
type Fields = typeof fieldList;
type SelectedField = {
  [key in Fields[number]]: boolean;
};
const selectedFields = ref<SelectedField>({});

const measureUnits = [
  { text: 'Unidades', value: 'unities' },
  { text: 'Caixas', value: 'boxes' },
  { text: 'Caixasde 9l', value: 'boxes-9l' },
];
const selectedMeasure = ref(measureUnits[0]);

const isExportLoading = ref(false);
const exportToExcel = () => {
  isExportLoading.value = true;
  setTimeout(() => {
    isExportLoading.value = false;
  }, 2000);
};
</script>

<style scoped>
h1 {
  color: #A30526;
}

h3 {
  color: #FFFFFF;
  font-size: 18px;
}

.btn-information {
  background-color: #A30526 !important;
  color: #FFFFFF !important;
}

.v-data-table__wrapper td:not(:last-child),
.v-data-table__wrapper th:not(:last-child) {
  border-right: 1px solid rgba(0, 0, 0, 0.12);
}
</style>

