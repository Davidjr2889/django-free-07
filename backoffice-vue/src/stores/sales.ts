import { defineStore } from 'pinia';
import { $fetch } from '@/plugins/fetch';
import { Product, ProductStock } from '@/types/common';

type Families = {
  [key: ProductStock['family']]: ProductStock
};

interface State {
  data: Families[];
}

export const useSalesStore = defineStore('sales', {
  state: (): State => ({
    data: [],
  }),

  actions: {
    async getSales () {
      try {
        const data = await $fetch('prev_log/sales', {
          method: 'GET',
        });

        this.data = Object.keys(data.products).map((key) => data.products[key]).flat(1) ?? [];
      } catch (error) {
        console.error(error);
      }
    },

    async getNewSalesTendencies (company: string, bo: string, family: string, article: string, base_anual: number) {
      try {
        const data = await $fetch('prev_log/sale/tendency/change', {
          method: 'GET',
          query: {
            company,
            bo,
            family,
            article,
            base_anual,
          },
        });

        this.data = Object.keys(data.products).map((key) => data.products[key]).flat(1) ?? [];
      } catch (error) {
        console.error(error);
      }
    },

    async putSales (product: Product, value: number): Promise<Product> {
      try {
        const data = await $fetch(`prev_log/sale/change/${product.id}`, {
          method: 'PUT',
          body: {
            value,
          },
        });

        return data?.products ?? [];
      } catch (error) {
        console.error(error);
      }
    },

    async postSales (product: Product): Promise<Product> {
      try {
        const data = await $fetch('prev_log/sale/change', {
          method: 'POST',
          body: {
            product,
          },
        });

        return data?.products ?? [];
      } catch (error) {
        console.error(error);
      }
    },

  },
});
