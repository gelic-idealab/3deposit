<template>
  <div id="app">
    <div class="container-fluid">
      <img alt="logo" src="./assets/logo.png" height="128" width="128">
      <Banner v-bind:title="form.title"/>
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
      .get('https://c78371d1-18dd-4567-b3c5-ec694cfe1d78.mock.pstmn.io/form')
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
