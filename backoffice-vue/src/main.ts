import Vue, { provide } from "vue";
import App from "./App.vue";
import router from "./router";

import { PiniaVuePlugin, createPinia } from "pinia";
import { useMainStore } from "./stores";

import VueFetch from "./plugins/fetch";

import config from "@/config";
import Notifications from "vue-notification";

import Icon from "vue-awesome/components/Icon.vue";
import "vue-awesome/icons/spinner";

import "@progress/kendo-ui";

import "@progress/kendo-ui/js/cultures/kendo.culture.pt-PT";
import "@progress/kendo-ui/js/messages/kendo.messages.pt-PT";

import { load, loadMessages } from "@progress/kendo-vue-intl";
import currencyData from "cldr-core/supplemental/currencyData.json";
import likelySubtags from "cldr-core/supplemental/likelySubtags.json";
import weekData from "cldr-core/supplemental/weekData.json";
import caGregorian from "cldr-dates-full/main/pt-PT/ca-gregorian.json";
import dateFields from "cldr-dates-full/main/pt-PT/dateFields.json";
import timeZoneNames from "cldr-dates-full/main/pt-PT/timeZoneNames.json";
import currencies from "cldr-numbers-full/main/pt-PT/currencies.json";
import numbers from "cldr-numbers-full/main/pt-PT/numbers.json";

load(
  likelySubtags,
  currencyData,
  weekData,
  numbers,
  currencies,
  caGregorian,
  dateFields,
  timeZoneNames,
);

const ptMessages = {
  datepicker: {
    toggleCalendar: "Alternar calendario",
  },
  calendar: {
    today: "Hoje",
  },
  dateinput: {
    increment: "Incrementar valor",
    decrement: "Diminuir valor",
  },
  numerictextbox: {
    increment: "Incrementar valor",
    decrement: "Diminuir valor",
  },
  grid: {
    groupPanelEmpty:
      "Arraste o título de uma coluna e solte-o aqui para agrupar por esse criterio",
    noRecords: "Não há dados disponíveis.",
    pagerFirstPage: "Ir para a primeira página",
    pagerPreviousPage: "Ir para a página anterior",
    pagerNextPage: "Ir para a página seguinte",
    pagerLastPage: "Ir para a última página",
    pagerPage: "Página",
    pagerOf: "de",
    pagerItems: "ítems",
    pagerInfo: "{0} - {1} de {2} ítems",
    pagerItemsPerPage: "ítems por página",
    filterEqOperator: "É igual a",
    filterNotEqOperator: "Não é igual a",
    filterIsNullOperator: "É nulo",
    filterIsNotNullOperator: "Não é nulo",
    filterIsEmptyOperator: "Está vazio",
    filterIsNotEmptyOperator: "Não está vazio",
    filterStartsWithOperator: "Começa com",
    filterContainsOperator: "Contêm",
    filterNotContainsOperator: "Não contem",
    filterEndsWithOperator: "Termina em",
    filterGteOperator: "É maior ou igual que",
    filterGtOperator: "É maior que",
    filterLteOperator: "É menor ou igual que",
    filterLtOperator: "É menor ou igual que",
    filterIsTrue: "Sim",
    filterIsFalse: "Não",
    filterBooleanAll: "(Todas)",
    filterAfterOrEqualOperator: "É posterior ou igual a",
    filterAfterOperator: "É posterior",
    filterBeforeOperator: "É anterior",
    filterBeforeOrEqualOperator: "É anterior ou igual a",
    filterSubmitButton: "Filtrar",
    filterClearButton: "Limpar",
    filterAndLogic: "E",
    filterOrLogic: "Ou",
    filterTitle: "Filtrar",
    sortDescending: "Ordem Crescente",
    sortAscending: "Ordem Decrescente",
  },
};
loadMessages(ptMessages, "pt-PT");

kendo.culture("pt-PT");
// eslint-disable-next-line vue/multi-word-component-names
Vue.component("icon", Icon);

Vue.use(Notifications);

Vue.config.productionTip = false;

Vue.use(VueFetch, {
  baseUrl: config.apiBaseUrl + "/",
});

Vue.use(PiniaVuePlugin);
const pinia = createPinia();

Vue.use(VueFetch)

async function main () {
  const mainPiniaStore = useMainStore(pinia);
  await mainPiniaStore.init();
  new Vue({
    setup () {
      provide("pinia-store", pinia);
    },
    router,
    pinia,
    render: (h) => h(App),
  }).$mount("#app");
}

main();
