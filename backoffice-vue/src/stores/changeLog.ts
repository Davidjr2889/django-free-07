import { $fetch } from "@/plugins/fetch";
import { defineStore } from "pinia";

export const useChangeLog = defineStore("changeLog", {
  state: () => ({
    data: [],
    page: 1,
    limitPage: 15,
    TotalPages: 1,
  }),
  actions: {
    async fetchData () {
      const { events } = await $fetch("prev_log/logs/", { method: "GET" });
      const convertObj = [];
      events.forEach(function (v, k) {
        v.qt_u = parseInt(v.qt_u)
        v.prev_qt_u = parseInt(v.prev_qt_u)
        v.mes = v.mes + "/" + v.ano
        convertObj.push(v);
      })
      this.data = convertObj
      this.TotalPages = Math.ceil(this.data.length / this.limitPage)
    },
    async fetchAllData () {
      const { events } = await $fetch("prev_log/logs/?showAll=true", { method: "GET" });
      const convertAllObj = [];
      events.forEach(function (v, k) {
        v.qt_u = parseInt(v.qt_u)
        v.prev_qt_u = parseInt(v.prev_qt_u)
        v.mes = v.mes + "/" + v.ano
        convertAllObj.push(v);
      })
      this.data = convertAllObj
      this.TotalPages = Math.ceil(this.data.length / this.limitPage)
    },
    currentPage (): number {
      return this.page;
    },
    perPage (): number {
      return this.limitPage
    },
    pageCount (): number {
      return this.TotalPages
    },
  },
});
