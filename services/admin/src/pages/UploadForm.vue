<template>
  <div id="uploadForm">
    <div class="container">
      <Banner v-bind:banner="form.banner"/>
      <Upload v-bind:id="id"/>
      <Fields v-bind:fields="form.fields" :id="id"/>
      <Footer />
    </div>
  </div>
</template>

<script>
import Banner from '../components/Banner.vue'
import Fields from '../components/Fields.vue'
import Upload from '../components/Upload.vue'
import Footer from '../components/Footer.vue'

import axios from 'axios'
import uuidv4 from 'uuid'

import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'


export default {
  name: 'app',
  components: {
    Banner,
    Fields,
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
      .get('../api/form', {params: {form_id: this.$route.params.id}})
      .then(response => (this.form = response.data.form.content));
    // eslint-disable-next-line
    console.log(this.id);
  },
}
</script>



<style>
#uploadForm {
  /*font-family: 'Avenir', Helvetica, Arial, sans-serif;*/
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
