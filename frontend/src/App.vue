<template>
  <div id="app">
    <ChartComponent />
  </div>
</template>

<script>
import ChartComponent from './components/processed_data.vue';

export default {
  name: 'App',
  components: {
    ChartComponent,
  },
};
</script>
