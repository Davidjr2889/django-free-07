import { defineStore } from 'pinia';
import { $fetch } from '@/plugins/fetch';
import { Product, UpdateRequest } from '@/types/common';

// Está definido um esqueleto de uma store a usar options, mas pode ser alterada para composition!

interface State {
  criticalStockProducts: Product[];
  criticalStockFamilies: Product[];
  noForecastFamilies: Product[];
  pendingRequests: UpdateRequest[];
  highDeviationFamilies: Product[];
}

export const useDashboardStore = defineStore('dashboard', {
  state: (): State => ({
    criticalStockProducts: [],
    criticalStockFamilies: [],
    noForecastFamilies: [],
    pendingRequests: [],
    highDeviationFamilies: [],
  }),

  actions: {
    async getCriticalStockProducts (groupBy: string|null = null) {
      try {
        if (groupBy) {
          groupBy = `?group_by=${groupBy}`;
        }
        const data = await $fetch(`prev_log/dashboard/stock${groupBy ?? ''}`, {
          method: 'GET',
        });
        if (groupBy) {
          this.criticalStockFamilies = Object.keys(data.products).map((key) => data.products[key]).flat(1) ?? [];
          ;
        } else {
          this.criticalStockProducts = Object.keys(data.products).map((key) => data.products[key]).flat(1) ?? [];
        }
      } catch (error) {
        console.error(error);
      }
    },

    async getNoForecastFamilies () {
      try {
        const data = await $fetch('prev_log/dashboard/forecast', {
          method: 'GET',
        });
        this.noForecastFamilies = Object.keys(data.products).map((key) => data.products[key]).flat(1) ?? [];
      } catch (error) {
        console.error(error);
      }
    },

    async getPendingRequests () {
      try {
        const data = await $fetch('prev_log/dashboard/pending', {
          method: 'GET',
        });
        this.pendingRequests = Object.keys(data.requests).map((key) => data.requests[key]).flat(1) ?? [];
      } catch (error) {
        console.error(error);
      }
    },

    async getHighDeviationFamilies () {
      try {
        const data = await $fetch('prev_log/dashboard/sale', {
          method: 'GET',
        });
        this.highDeviationFamilies = Object.keys(data.products).map((key) => data.products[key]) ?? [];
      } catch (error) {
        console.error(error);
      }
    },

  },
});
