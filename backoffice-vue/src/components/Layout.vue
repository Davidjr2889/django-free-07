<template>
  <div>
    <slot name="header" aria-label="breadcrumb">
      <h1 class="text-start pb-4 px-2">Previsões de Vendas</h1>
    </slot>

    <slot name="actions"></slot>

    <slot name="content"></slot>
  </div>
</template>
