import { defineStore } from "pinia";
import { $fetch } from "@/plugins/fetch";
import { Product, ProductStock } from "@/types/common";

type Families = {
  [key: ProductStock["family"]]: ProductStock;
};

interface State {
  data: Families[];
  dataHistory: Families[];
  dataForecast: Families[];
}

export const useSalesForecastStore = defineStore("sales-forecast", {
  state: (): State => ({
    data: [],
    dataHistory: [],
    dataForecast: [],
  }),

  actions: {
    async getSalesForecast() {
      try {
        const data = await $fetch("prev_log/sales", {
          method: "GET",
        });

        this.data =
          Object.keys(data.products)
            .map((key) => data.products[key])
            .flat(1) ?? [];

        this.dataHistory = Object.keys(data.products)
          .map((key) => data.products[key].history)
          .flat(1)
          .filter((history) => history !== undefined);

        this.dataForecast = Object.keys(data.products)
          .map((key) => data.products[key].forecast)
          .flat(1)
          .filter((forecast) => forecast !== undefined);
      } catch (error) {
        console.error(error);
      }
    },

    async getNewSalesTendencies(
      company: string,
      bo: string,
      family: string,
      article: string,
      base_anual: number
    ) {
      try {
        const data = await $fetch("prev_log/sale/tendency/change", {
          method: "GET",
          query: {
            company,
            bo,
            family,
            article,
            base_anual,
          },
        });

        this.data =
          Object.keys(data.products)
            .map((key) => data.products[key])
            .flat(1) ?? [];
      } catch (error) {
        console.error(error);
      }
    },

    async putSalesForecast(product: Product, value: number): Promise<Product> {
      try {
        const data = await $fetch(`prev_log/sale/change/${product.id}`, {
          method: "PUT",
          body: {
            value,
          },
        });

        return data?.products ?? [];
      } catch (error) {
        console.error(error);
      }
    },

    async postSalesForecast(product: Product): Promise<Product> {
      try {
        const data = await $fetch("prev_log/sale/change", {
          method: "POST",
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
