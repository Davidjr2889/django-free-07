import { defineStore } from 'pinia';
import { $fetch } from '@/plugins/fetch';
import { Product, ProductStock } from '@/types/common';

type Families = {
  [key: ProductStock['family']]: ProductStock
};

interface State {
  data: Families[];
}

export const useStockStore = defineStore('stocks', {
  state: (): State => ({
    data: [],
  }),

  actions: {
    async getStockProducts () {
      try {
        const data = await $fetch('prev_log/stocks', {
          method: 'GET',
        });

        this.data = Object.keys(data.products).map((key) => data.products[key]).flat(1) ?? [];
      } catch (error) {
        console.error(error);
      }
    },

    async putStockProduct (product: Product, value: number): Promise<Product> {
      try {
        const data = await $fetch(`prev_log/stock/change/${product.id}`, {
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

    async postStockProduct (product: Product): Promise<Product> {
      try {
        const data = await $fetch('prev_log/stock/change', {
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
