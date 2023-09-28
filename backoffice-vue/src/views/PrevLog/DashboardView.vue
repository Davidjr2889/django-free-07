<!-- eslint-disable vue/valid-v-slot -->
<template>
  <div class="container text-center">
    <h1 class="text-start pb-4 px-2">Dashboard</h1>
    <div class="row">
      <div class="col-6">
        <Grid ref="grid" :style="{ height: '250px' }" :data-items="criticalStockFamilies" :reorderable="true"
          :sortable="true" :groupable="false" :group="['family']" :take="10" :skip="0" :expand-field="'expanded'"
          :columns="criticalStockFamiliesFields" :loader="false" @datastatechange="dataStateChange"
          @expandchange="expandChange">
        </Grid>
      </div>

      <div class="col-6">
        <!-- <v-card class="overflow-hidden">
          <v-card-title>
            <h3 class="m-0 mx-auto p-0 text-center fw-semibold">Produtos com estoque crítico</h3>
          </v-card-title>
          <v-data-table class="elevation-1 overflow-x-auto" dense :headers="criticalStockProductsFields"
            :items="criticalStockProducts" item-key="name" fixed-header height="250px">
            <template v-slot:item="props">
              <tr>
                <td>{{ props.item.descricao }}</td>
                <td>{{ props.item.artigo }}</td>
                <td :class="getColor(props.item.stock_actual)">{{ props.item.stock_actual }}</td>
              </tr>
            </template>
          </v-data-table>
          <v-card-actions>
            <v-spacer></v-spacer>
            <router-link :to="{ path: '/stocks' }" class="text-sm-end">
              Abrir previsão de estoque completo
              <span class="k-icon k-i-arrow-right"></span>
            </router-link>
          </v-card-actions>
        </v-card> -->
      </div>
    </div>
    <div class="row">
      <div class="col-6">
        <!-- <v-card class="overflow-hidden">
          <v-card-title>
            <h3 class="m-0 mx-auto p-0 text-center fw-semibold">Famílias e Produtos sem previsão</h3>
          </v-card-title>
          <v-data-table class="elevation-1 overflow-x-auto" dense :headers="noForecastFamiliesFields"
            :items="noForecastFamilies" item-key="name" fixed-header height="250px" group-by="family">
            <template v-slot:group.header="{ items, isOpen, toggle }">
              <th :colspan="items.length" class="text-start">
                {{ items[0].family }}
                <v-icon small @click="toggle">{{ isOpen ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
              </th>
            </template>
          </v-data-table>
          <v-card-actions>
            <v-spacer></v-spacer>
            <router-link :to="{ path: '/sales' }" class="text-sm-end">
              Abrir previsão de vendas completo
              <span class="k-icon k-i-arrow-right"></span>
            </router-link>
          </v-card-actions>
        </v-card> -->
      </div>

      <div class="col-6">
        <!-- <v-card class="overflow-hidden">
          <v-card-title>
            <h3 class="m-0 mx-auto p-0 text-center fw-semibold">Pedidos pendentes</h3>
          </v-card-title>
          <v-data-table class="elevation-1 overflow-x-auto" dense :headers="pendingRequestsFields"
            :items="pendingRequests" item-key="name" fixed-header height="250px" group-by="product.family">
            <template v-slot:group.header="{ items, isOpen, toggle }">
              <th :colspan="items.length" class="text-start">
                {{ items[0].product.family }}
                <v-icon small @click="toggle">{{ isOpen ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
              </th>
            </template>
          </v-data-table>
          <v-card-actions>
            <v-spacer></v-spacer>
            <router-link :to="{ path: '/change_log' }" class="text-sm-end">
              Abrir Log de pedidos de alteração
              <span class="k-icon k-i-arrow-right"></span>
            </router-link>
          </v-card-actions>
        </v-card> -->
      </div>
    </div>
    <div class="row">
      <div class="col-6">
        <!-- <v-card class="overflow-hidden">
          <v-card-title>
            <h3 class="m-0 mx-auto p-0 text-center fw-semibold">Família e Produtos com desvio elevado</h3>
          </v-card-title>
          <v-data-table class="elevation-1 overflow-x-auto" dense :headers="highDeviationFamiliesFields"
            :items="highDeviationFamilies" item-key="name" fixed-header height="250px" group-by="family">
            <template v-slot:group.header="{ items, isOpen, toggle }">
              <th :colspan="3" class="text-start">
                {{ items[0].family }}
                <v-icon small @click="toggle">{{ isOpen ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
              </th>
            </template>
          </v-data-table>
        </v-card> -->
      </div>

      <div class="col-6"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useDashboardStore } from '@/stores/dashboard';
import { DataTableHeader } from '@/types/common';
import { Grid } from '@progress/kendo-vue-grid';

const dashboardStore = useDashboardStore();
dashboardStore.getCriticalStockProducts();
dashboardStore.getCriticalStockProducts('family');
dashboardStore.getNoForecastFamilies();
dashboardStore.getPendingRequests();
dashboardStore.getHighDeviationFamilies();

const criticalStockProductsFields: DataTableHeader[] = [
  { text: 'Produto', value: 'descricao', class: 'bg-dark' },
  { text: 'SKU', value: 'artigo', class: 'bg-dark' },
  { text: 'Stock', value: 'stock_actual', class: 'bg-dark' },
];
const criticalStockProducts = computed(() => dashboardStore.criticalStockProducts);

const criticalStockFamiliesFields: DataTableHeader[] = [
  { text: 'Família', value: 'familia', class: 'bg-dark', cellClass: 'with-divider' },
  { text: 'Produto', value: 'descricao', class: 'bg-dark', cellClass: 'with-divider' },
  { text: 'SKU', value: 'artigo', class: 'bg-dark', cellClass: 'with-divider' },
  { text: 'Stock', value: 'stock_actual', class: 'bg-dark', cellClass: 'with-divider' },
];
const criticalStockFamilies = computed(() => dashboardStore.criticalStockFamilies);

const noForecastFamiliesFields: DataTableHeader[] = [
  { text: 'Família', value: 'family', class: 'bg-dark' },
  { text: 'Produto', value: 'description', class: 'bg-dark' },
  { text: 'SKU', value: 'article', class: 'bg-dark' },
];
const noForecastFamilies = computed(() => dashboardStore.noForecastFamilies);

const pendingRequestsFields: DataTableHeader[] = [
  { text: 'Família', value: 'product.familia', class: 'bg-dark' },
  { text: 'Família', value: 'product.descricao', class: 'bg-dark' },
  { text: 'Utilizador', value: 'user', class: 'bg-dark' },
  { text: 'Data da solicitação', value: 'requestDate', class: 'bg-dark' },
  { text: 'Quant. Anterior', value: 'quantity', class: 'bg-dark' },
  { text: 'Quant. Alterada', value: 'quantityNew', class: 'bg-dark' },
  { text: 'Entidade', value: 'entity', class: 'bg-dark' },
];
const pendingRequests = computed(() => dashboardStore.pendingRequests);

const highDeviationFamiliesFields: DataTableHeader[] = [
  { text: 'Família', value: 'family', class: 'bg-dark' },
  { text: 'Produto', value: 'description', class: 'bg-dark' },
  { text: 'SKU', value: 'article', class: 'bg-dark' },
  { text: 'Stock', value: 'stock', class: 'bg-dark' },
];
const highDeviationFamilies = computed(() => dashboardStore.highDeviationFamilies);

const getColor = (stock: number) => {
  if (stock <= 0) return 'cell-danger';
  if (stock <= 5) return 'cell-warning';
  // return 'cell-success';
};

const dataStateChange = () => {
  dashboardStore.getCriticalStockProducts('family');
};

const expandChange = (event: any) => {
  event.dataItem[event.target.$props.expandField] = event.value;
  //
  // In Vue 2 context, instead of the above line, inside the expandChange method we should have the following:
  //
  //   Vue.set(
  //     event.dataItem,
  //     event.target.$props.expandField,
  //     event.dataItem.expanded === undefined ? false : !event.dataItem.expanded
  //   );
  //
};
</script>

<style scoped lang="scss">
@import '../../shared/custom.scss';

h1 {
  color: #dd052b;
}

.cell-danger {
  background-color: $brand-danger;
  color: #212121;
}

.cell-warning {
  background-color: $brand-warning;
  color: #212121;
}

.cell-success {
  background-color: $brand-success;
  color: #212121;
}

div.v-card__title {
  background-color: #212121;
}

h3 {
  color: #FFFFFF;
  font-size: 18px;
}

a {
  color: #dd052b;
  text-decoration: none;
}

a:hover {
  color: #cf3257;
}

.table-responsive {
  margin: 0;
}

.v-data-table__wrapper td:not(:last-child),
.v-data-table__wrapper th:not(:last-child) {
  border-right: 1px solid rgba(0, 0, 0, 0.12);
}
</style>
