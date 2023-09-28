<template>
  <div class="app" data-app>
    <IntlProvider :locale="'pt-PT'">
      <main-menu></main-menu>
    </IntlProvider>
  </div>
</template>

<script setup lang="ts">
import { defineComponent } from "vue";
import MainMenu from "./components/MainMenu.vue";
import { IntlProvider } from "@progress/kendo-vue-intl";

defineComponent({
  components: {
    MainMenu,
    IntlProvider,
  },
});
</script>

<style lang="scss">
@import "./shared/custom";
@import "./node_modules/bootstrap/scss/bootstrap";
@import "./node_modules/@progress/kendo-theme-bootstrap/dist/all.scss";
@import "./views/lbarm";

.container {
  margin: 40px;
}

html,
body {
  height: 100%;
  font-family: Arial, Helvetica, sans-serif;
}

body {
  margin: 0;
}

span.active {
  background-color: gray;
}

.col-xs {
  flex-basis: 0;
  flex-grow: 1;
  max-width: 100%;
}

.col-xs-12 {
  flex: 0 0 100%;
}

.nav-toggle .k-i-hamburger {
  font-size: 32px;
}

/* Classes removidas no Bootstrap 5 */

.form-group {
  margin-bottom: 1rem;
}

.form-inline .form-control {
  display: inline-block;
  width: auto;
  vertical-align: middle;
}

.form-row {
  display: flex;
  flex-wrap: wrap;
  margin-right: -5px;
  margin-left: -5px;
}

label {
  margin-bottom: 0.5rem;
}

.bg-dark {
  color: #ffffff !important;
  background-color: #1f2121 !important;
}

td.text-center {
  margin: 0px;
}

.customer-photo {
  display: inline-block;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-size: 32px 35px;
  background-position: center center;
  vertical-align: middle;
  line-height: 32px;
  box-shadow: inset 0 0 1px #999, inset 0 0 10px rgba(0, 0, 0, 0.2);
  margin-left: 5px;
}

.customer-name {
  display: inline-block;
  vertical-align: middle;
  line-height: 32px;
  padding-left: 10px;
}

.red {
  color: #d9534f;
}

.text-bold {
  font-weight: 600;
}

.export-buttons {
  margin-left: auto;
  margin-right: 0;
}

.localeDropDownList {
  margin-right: 5px;
}

h1 {
  color: #a30526;
}

h3 {
  color: #ffffff;
  font-size: 18px;
}

.btn-information {
  background-color: #a30526 !important;
  color: #ffffff !important;
}

.v-data-table__wrapper td:not(:last-child),
.v-data-table__wrapper th:not(:last-child) {
  border-right: 1px solid rgba(0, 0, 0, 0.12);
}
</style>
