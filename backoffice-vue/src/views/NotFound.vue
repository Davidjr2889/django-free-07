<template>
  <main class="not-found more-info">
    <h1>Página não encontrada</h1>
    <p class="more-info">
      Não é possível encontrar a página que procura.<br/>
      Poderá ter sido movida, apagada ou estar ainda em desenvolvimento.<br/>
      Verifique o endereço ou 'clique' no botão abaixo para voltar para a página inicial.
    </p>
    <div class="actions">
      <router-link tag="button" :to="{name: 'home'}">Voltar à página inicial</router-link>
    </div>
  </main>
</template>

<style>
.more-info {
  text-align: center;
}
</style>
