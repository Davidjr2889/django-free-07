import { defineStore } from 'pinia';
import { $fetch } from '@/plugins/fetch';

// Está definido um esqueleto de uma store a usar options, mas pode ser alterada para composition!

interface State {

}

export const usePrevLogStore = defineStore('prevLog', {

  state: (): State => ({

  }),

  actions: {
  },

});
