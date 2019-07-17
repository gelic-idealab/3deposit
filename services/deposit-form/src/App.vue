<template>
  <div id="app">
    <div class="container-fluid">
      <img alt="logo" src="./assets/logo.png" height="128" width="128">
      <Banner v-bind:banner="form.banner"/>
      <!-- <FileProgress v-bind:id="id"/> -->
      <Upload v-bind:id="id"/>
      <Fields v-bind:fields="form.fields" :id="id"/>
    </div>
  </div>
</template>

<script>
import Banner from './components/Banner.vue'
import Fields from './components/Fields.vue'
// import FileProgress from './components/FileProgress.vue'
import Upload from './components/Upload.vue'
import 'bootstrap/dist/css/bootstrap.min.css'
import axios from 'axios'
import uuidv4 from 'uuid'


export default {
  name: 'app',
  components: {
    Banner,
    Fields,
    // FileProgress,
    Upload
  },
  data() {
    return {
      form: {"banner": {}, "fields": []},
      id: uuidv4()
    }
  },
  mounted () {
    axios
      .get('../api/form')
      .then(response => (this.form = response.data.form.content));
    // eslint-disable-next-line
    console.log(this.id);
  },
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
