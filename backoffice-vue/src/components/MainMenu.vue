<template>
  <div class="row h-100">
    <notifications group="lbbackoffice" />
    <div
      id="top-bar"
      v-if="router.currentRoute.path.toLowerCase() !== '/login'"
      class="top-bar col-12 bg-inverse d-lg-none"
    ></div>
    <div
      id="nav"
      class="col bg-inverse text-white pb-3 k-vbox"
      v-if="router.currentRoute.path.toLowerCase() !== '/login'"
      :class="{ expand: navState }"
    >
      <div id="app-logo" class="text-center pb-5">
        <h3 class="pt-5 app-title text-center" id="app-title">Backoffice</h3>
        <p id="app-version" style="width: 100%; text-align: center">V-DEV</p>
      </div>

      <span
        id="nav-toggle"
        class="nav-toggle d-lg-none"
        @click="navState = !navState"
      >
        <span class="k-icon k-i-hamburger"></span>
      </span>

      <template v-if="viewDevModule">
        <p
          class="h4 nav-collapsable d-flex justify-content-between"
          :class="{ open: isOpen.devModule, 'link-active': devModuleActive }"
          @click="isOpen.devModule = !isOpen.devModule"
        >
          <span>Previsão Logística</span>
          <span>{{ icon(isOpen.devModule) }}</span>
        </p>
        <ul
          class="nav nav-pills nav-collapsable-menu flex-column"
          v-show="isOpen.devModule"
        >
          <!-- <li class="nav-item" id="dev_list" v-if="userCanAccess('prev_mod')">
            <router-link to="/prev_log" class="nav-link">Previsão Logística</router-link>
          </li> -->
          <li class="nav-item" id="dashboard">
            <router-link to="/dashboard" class="nav-link"
              >Dashboard</router-link
            >
          </li>
          <li
            class="nav-item"
            id="sales-forecast"
            v-if="userCanAccess(Permission.SALES_FORECAST)"
          >
            <router-link to="/sales-forecast" class="nav-link"
              >Previsão de Vendas</router-link
            >
          </li>
          <li
            class="nav-item"
            id="sales"
            v-if="userCanAccess(Permission.SALES)"
          >
            <router-link to="/sales" class="nav-link">Vendas</router-link>
          </li>
          <li
            class="nav-item"
            id="stocks"
            v-if="userCanAccess(Permission.STOCK)"
          >
            <router-link to="/stocks" class="nav-link">Estoque</router-link>
          </li>
          <li
            class="nav-item"
            id="purchases"
            v-if="userCanAccess(Permission.PURCHASE)"
          >
            <router-link to="/purchases" class="nav-link">Compras</router-link>
          </li>
          <li
            class="nav-item"
            id="order-summary"
            v-if="userCanAccess(Permission.ORDER_SUMMARY)"
          >
            <router-link to="/orders-summary" class="nav-link"
              >Resumo de Ordens</router-link
            >
          </li>
          <li
            class="nav-item"
            id="dev_list"
            v-if="userCanAccess(Permission.CHANGE_LOG)"
          >
            <router-link to="/change_log" class="nav-link"
              >Log de alteracao</router-link
            >
          </li>
        </ul>
      </template>

      <p
        class="h4 nav-collapsable d-flex justify-content-between"
        :class="{ open: isOpen.account }"
        @click="isOpen.account = !isOpen.account"
      >
        <span>Account</span>
        <span>{{ icon(isOpen.account) }}</span>
      </p>
      <ul
        class="nav nav-pills nav-collapsable-menu flex-column"
        v-show="isOpen.account"
      >
        <li class="nav-item" id="logout">
          <router-link to="/logout" class="nav-link"
            >Logout ({{ username }})</router-link
          >
        </li>
      </ul>

      <hr class="k-flex" />
    </div>

    <main
      class="px-0 ms-4"
      :class="{
        'col-12': currentRoute === '/login',
        'col-12 col-md': currentRoute !== '/login',
      }"
    >
      <router-view class="mt-0"></router-view>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useMainStore } from "@/stores";
import router from "@/router";
import { Permission } from "@/types/common/permissions";
// import { userCanAccess as canAccess } from '@/shared/permissions.coffee';

const mainStore = useMainStore();

const navState = ref(false);
const isOpen = ref({
  devModule: false,
  account: false,
});

const username = computed(() => {
  return mainStore.username;
});

// const isAdminUser = computed(() => {
//   return mainStore.isAdminUser;
// });

const currentRoute = computed(() => {
  return router.currentRoute.path.toLowerCase();
});

const viewDevModule = computed(() => {
  return true;
});

const userCanAccess = (module: Permission) => {
  if (module) {
    return true;
  }
  return true;
};

const devModuleActive = computed(() => {
  return /\/dev_/.test(router.currentRoute.path);
});

const icon = computed(() => {
  return (state: boolean) => (state ? "–" : "+");
});
</script>

<style>
.bg-inverse {
  background-color: #292b2c !important;
}

a.bg-inverse:focus,
a.bg-inverse:hover {
  background-color: #101112 !important;
}
</style>
