<!-- eslint-disable vue/valid-v-slot -->
<template>
  <div>
    <div class="text-start p-4">
      <Button
        @click.native="$router.push({ name: 'sales-forecast' })"
        text="Voltar"
        icon="arrow-left"
      />
    </div>
    <div class="text-center">
      <div class="row">
        <div class="tasks p-4">
          <Layout>
            <template #content>
              <div class="table-container">
                <Table
                  :search="search"
                  :data="fetchAll"
                  :columns="headers"
                  class="table"
                  toolbar-text="Informacoes de produtos"
                  toolbar-color="#292b2c"
                  :sortable="true"
                />
              </div>
            </template>
          </Layout>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useChangeLog } from "@/stores/changeLog";
import Table from "@/components/Table.vue";
import Layout from "@/components/Layout.vue";
import Button from "@/components/Button.vue";
import { ref, computed } from "vue";
import { DataTableHeader } from "@/types/common";

const search = ref("");

const getLog = useChangeLog();
getLog.fetchData();
getLog.pageCount();
getLog.perPage();
const fetchAll = computed(() => getLog.data);

const headers: DataTableHeader[] = [
  { title: "Utilizador", align: "start", sortable: false, field: "utilizador" },
  {
    title: "Data e hora da alteração do pedido",
    sortable: false,
    field: "created_at",
  },
  { title: "Mes/Ano da previsao", sortable: false, field: "mes" },
  { title: "Família", sortable: false, field: "familia" },
  { title: "Artigo", sortable: false, field: "artigo" },
  { title: "Qtd.anterior", sortable: false, field: "prev_qt_u" },
  { title: "Qtd.Atual", sortable: false, field: "qt_u" },
  { title: "Comentário", sortable: false, field: "comentario" },
  { title: "Status", sortable: false, field: "status" },
  { title: "Origem", sortable: false, field: "origem_forecast" },
];
</script>

<style>
.v-data-table-header > tr > th > span {
  color: white;
  font-weight: bold;
}

.v-data-table-header {
  background: black;
}

th.k-header.active > div > div {
  color: #fff;
  background-color: #92031c;
}

.container-table {
  background-color: #fff;
  padding: 4em;
  color: rgba(0, 0, 0, 0.87);
}

.title-container {
  font-size: 2em;
  margin-bottom: 1em;
  color: #bd1010;
  font-weight: bold;
}

.theme--light.v-pagination .v-pagination__item--active {
  color: rgba(0, 0, 0, 0.87) !important;
  background: #babaf7 !important;
}
</style>
