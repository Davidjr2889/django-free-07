import { defineStore } from 'pinia';
import { $fetch } from '@/plugins/fetch';
import { Product, ProductStock } from '@/types/common';

type Families = {
  [key: ProductStock['family']]: ProductStock
};

interface State {
  data: Families[];
}

export const usePurchaseStore = defineStore('purchase', {
  state: (): State => ({
    data: [],
  }),

  actions: {
    async getPurchases () {
      try {
        const data = await $fetch('prev_log/purchases', {
          method: 'GET',
        });

        this.data = Object.keys(data.products).map((key) => data.products[key]).flat(1) ?? [];
      } catch (error) {
        console.error(error);
      }
    },

    async putPurchase (product: Product, value: number): Promise<Product> {
      try {
        const data = await $fetch(`prev_log/purchase/change/${product.id}`, {
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

    async postPurchase (product: Product): Promise<Product> {
      try {
        const data = await $fetch('prev_log/purchase/change', {
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
