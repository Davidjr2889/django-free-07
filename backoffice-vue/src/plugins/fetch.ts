import _Vue from "vue";
import { useMainStore } from "@/stores";
import router from "@/router";
import config from "@/config";

let baseUrl: string;

export async function $fetch (url: string, options = {}, msTimeout = 10000) {
  const finalOptions: any = Object.assign(
    {},
    {
      credentials:
        process.env.NODE_ENV !== "production" ? "include" : "same-origin",
      headers: {
        "Content-Type": "application/json",
      },
    },
    msTimeout,
    options,
  );

  const store = useMainStore();
  const token = store.token;
  if (token !== null) {
    finalOptions.headers.Authorization = `Bearer ${token}`;
  }
  let response = null;
  try {
    response = await fetch(`${config.apiBaseUrl}/${url}`, finalOptions);
  } catch (e: any) {
    const error: any = new Error(e.message);
    error.status = 504;
    throw error;
  }
  if (response.ok) {
    const data = await response.json();
    return data;
  } else if (response.status === 401) {
    store.logout();
    router.replace({
      name: "Login",
      params: {
        wantedRoute: "/",
      },
    });
  } else {
    const message = await response.text();
    const error: any = new Error(message);
    error.response = response;
    error.status = response.status;
    throw error;
  }
}

export default {
  install (Vue: typeof _Vue, options?: any): void {
    baseUrl = options.baseUrl;
    Vue.prototype.$fetch = $fetch;
  },
};
