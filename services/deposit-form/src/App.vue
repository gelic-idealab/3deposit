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
      form: {}
    }
  },
  mounted () {
    axios
      .get('https://9bb92562-b7e9-4d42-bf6f-1885eae2ec34.mock.pstmn.io/formJSON')
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
