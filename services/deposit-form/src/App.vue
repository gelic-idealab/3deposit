<template>
  <div id="app">
    <div class="container-fluid">
      <img alt="logo" src="./assets/logo.png" height="128" width="128">
      <Banner v-bind:banner="form.banner"/>
      <Fields v-bind:fields="form.fields"/>
    </div>
  </div>
</template>

<script>
import Banner from './components/Banner.vue'
import Fields from './components/Fields.vue'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-toggle/css/bootstrap-toggle.min.css'
import axios from 'axios'
import 'bootstrap'


export default {
  name: 'app',
  components: {
    Banner,
    Fields
  },
  data() {
    return {
      form: {"banner": {}, "fields": []}
    }
  },
  mounted () {
    axios
      .get('https://01fd7a12-f268-409c-a89a-7d279e598b98.mock.pstmn.io/renderForm')
      .then(response => (this.form = response.data))
  }
}
</script>

<style>
#app {
  /*font-family: 'Avenir', Helvetica, Arial, sans-serif;*/
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
