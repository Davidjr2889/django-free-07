<template>
  <div id="signin" class="signin w-100">
    <div class="signin-form row align-items-center text-center">
      <div class="col-12 p-0">

        <h2 class="app-title mb-5" id="app-title">BACKOFFICE</h2>

        <p class="signin-subtitle mb-4" id="app-subtitle">Login</p>

        <div v-if="loginError" class="alert alert-danger mx-4 signin-errors" role="alert"><span
            class="k-icon k-i-warning mr-1"></span>&nbsp;Ocorreu um erro a fazer o login</div>

        <form @submit.prevent="submit">

          <div class="form-group my-4">

            <div class="signin-input-wrapper">
              <span class="signin-icon k-icon k-i-user"></span>
              <input type="text" name="username" v-model="username" class="form-control form-control-lg signin-input"
                placeholder="Username" />
            </div>

            <div class="signin-input-wrapper">
              <span class="signin-icon k-icon k-i-lock"></span>
              <input type="password" name="password" v-model="password" class="form-control form-control-lg signin-input"
                placeholder="Password" />
            </div>

          </div>

          <div class="form-group mt-5">
            <button class="btn btn-primary btn-lg w-50 text-uppercase signin-submit mx-auto">Log in</button>
            <p class="text-xs-right text-center small mt-2">
              <!-- <a class="signin-forget" href="#">Esqueceu a password?</a> -->
            </p>
          </div>

        </form>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import router from '@/router';
import { useMainStore } from '@/stores';

const loginError = ref(false);
const username = ref('');
const password = ref('');
const mainStore = useMainStore();

const submit = async () => {
  try {
    const success = await mainStore.login(username.value, password.value);
    if (success) {
      router.replace(
        { name: router.currentRoute.params?.wantedRoute as string ?? 'Home' },
      );
    }
  } catch (e) {
    console.log(e);
    loginError.value = true;
  }
}
</script>
