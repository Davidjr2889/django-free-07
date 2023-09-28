<template>
  <div>
    <Grid
      :data-items="gridData"
      :sortable="sortable"
      :pageable="gridPageable"
      :pageSize="take"
      :take="take"
      :total="filteredData.length"
      :skip="skip"
      :columns="columns"
      :group="group"
      @pagechange="pageChangeHandler"
      :noDataMessage="'Nenhum dado disponivel'"
      :loading="loader"
    >
      <template v-slot:myTemplate="{ props }">
        <custom
          :field="props.field"
          :expanded="props.expanded"
          :row-type="props.rowType"
          :level="props.level"
          :column-index="props.columnIndex"
          :columns-count="props.columnsCount"
          :data-item="props.dataItem"
          :class-name="props.className"
          @click="clickHandler(props.dataItem)"
        />
      </template>
    </Grid>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, toRef } from "vue";
import { process } from "@progress/kendo-data-query";
import { Grid } from "@progress/kendo-vue-grid";

const props = defineProps<{
  data: Array<object>;
  columns: Array<Column>;
  sortable?: boolean;
  search: string;
}>();

const search = toRef(props, "search");

const loader = ref(false);
const take = ref(40);
const skip = ref(0);
const gridPageable = ref({
  buttonCount: 5,
  info: true,
  type: "numeric",
  pageSizes: true,
  previousNext: true,
});

const filteredData = computed(() => {
  let filtered = props.data;

  if (search.value) {
    filtered = filtered.filter((item: any) =>
      Object.values(item).some(
        (value) =>
          value &&
          value.toString().toLowerCase().includes(search.value.toLowerCase())
      )
    );
  }

  return filtered;
});

const clickHandler = (dataItem) => {
  console.log(dataItem);
  dataItem.expanded =
    dataItem.expanded === undefined ? false : !dataItem.expanded;
};

const pageChangeHandler = (event) => {
  loader.value = true;
  setTimeout(() => {
    loader.value = false;
    skip.value = event.page.skip;
  }, 300);
};

const group = ref([{ field: "family", aggregates: [] }]);

const gridData = ref([]);

const getData = () => {
  gridData.value = process(filteredData.value, {
    take: take.value,
    skip: skip.value,
    group: group.value,
  });
};

getData();
</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: center;
  color: #fff;
}

.toolbar > span {
  font-size: 16px;
}
</style>
