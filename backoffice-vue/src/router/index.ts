import Vue from "vue";
import Router from "vue-router";

import DashboardView from "../views/PrevLog/DashboardView.vue";
import SalesView from "../views/PrevLog/SalesView.vue";
import SalesForecastView from "../views/PrevLog/SalesForecastView.vue";
import StockView from "../views/PrevLog/StockView.vue";
import PurchaseView from "../views/PrevLog/PurchaseView.vue";
import ChangeLog from "../views/PrevLog/ChangeLog.vue";
import OrderSummaryView from "../views/PrevLog/OrderSummaryView.vue";

import Login from "@/views/Login.vue";
import NotFound from "@/views/NotFound.vue";
import PrevLog from "@/views/PrevLog/PrevLog.vue";
import { useMainStore } from "@/stores";
import { Permission } from "@/types/common/permissions";

Vue.use(Router);

const router = new Router({
  mode: "history",
  base: "/backoffice",
  routes: [
    {
      path: "/login",
      name: "login",
      component: Login,
    },
    {
      path: "/logout",
      name: "logout",
      async beforeEnter (to: any, from: any, next: any) {
        // console.log("logout to: ", to.name);
        const mainStore = useMainStore();
        next({
          name: "login",
          params: {
            wantedRoute: "/",
          },
          from,
        });
        mainStore.logout();
      },
    },
    {
      path: "/prev-log",
      name: "prev-log",
      component: PrevLog,
      meta: {
        requiresAuth: true,
        permission: Permission.PREV_LOG,
      },
    },
    {
      path: "/",
      name: "home",
      component: DashboardView,
      meta: { requiresAuth: true },
    },
    {
      path: "/dashboard",
      name: "dashboard",
      component: DashboardView,
      meta: { requiresAuth: true },
    },
    {
      path: "/sales-forecast",
      name: "sales-forecast",
      component: SalesForecastView,
      meta: { requiresAuth: true },
    },
    {
      path: "/sales",
      name: "sales",
      component: SalesView,
      meta: { requiresAuth: true },
    },
    {
      path: "/stocks",
      name: "stocks",
      component: StockView,
      meta: { requiresAuth: true },
    },
    {
      path: "/purchases",
      name: "purchases",
      component: PurchaseView,
      meta: { requiresAuth: true },
    },
    {
      path: "/orders-summary",
      name: "orders-summary",
      component: OrderSummaryView,
      meta: { requiresAuth: true },
    },
    {
      path: "/change_log",
      name: "Logs de alteracoes",
      component: ChangeLog,
      meta: { requiresAuth: true },
    },
    {
      path: "*",
      component: NotFound,
    },
  ],
  linkActiveClass: "active",
});

router.beforeEach((to: any, from: any, next: any) => {
  // console.log("to", to.name);
  const mainStore = useMainStore();
  if (
    to.matched.some((r: any) => r.meta.requiresAuth) &&
    !mainStore.isAuthenticated
  ) {
    next({
      name: "login",
      params: {
        wantedRoute: to.fullPath,
      },
      from,
    });
    return;
  }

  next();
});

export default router;
