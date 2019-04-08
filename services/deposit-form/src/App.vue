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
import axios from 'axios'

export default {
  name: 'app',
  components: {
    Banner,
    Fields
  },
  data() {
    return {
      form: {}
      // mock api - https://1fd4d90a-5118-4b43-bd7d-4c481a1c2f51.mock.pstmn.io/getFormObject
    }
  },
  mounted () {
    axios
      .get('https://9c18a634-98c7-4ab4-af5c-a393934bd5f6.mock.pstmn.io/getFormObject')
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
