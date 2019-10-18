<template>
  <div id="app">
    <div class="container">
      <Banner v-bind:banner="form.banner"/>
      <!-- <FileProgress v-bind:id="id"/> -->
      <Upload v-bind:id="id"/>
      <Fields v-bind:fields="form.fields" :id="id"/>
      <Footer />
    </div>
  </div>
</template>

<script>
import Banner from './components/Banner.vue'
import Fields from './components/Fields.vue'
// import FileProgress from './components/FileProgress.vue'
import Upload from './components/Upload.vue'
import Footer from './components/Footer.vue'

import axios from 'axios'
import uuidv4 from 'uuid'

import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'


export default {
  name: 'app',
  components: {
    Banner,
    Fields,
    // FileProgress,
    Footer,
    Upload
  },
  data() {
    return {
      finished_uploading: false,
      form: {"banner": {}, "fields": []},
      id: uuidv4()
    }
  },
  mounted () {
    axios
      .get('../api/form', {params: {form_id: 'deposit_form'}})
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
  color: #2c3e50;
  margin-top: 60px;
}
</style>
