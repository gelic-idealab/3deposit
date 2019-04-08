<template>
  <div id="app">
    <div class="container-fluid">
      <img alt="3deposit logo" src="./assets/logo.png" height="128" width="128">
      <Banner msg="Deposit Form"/>
      <Fields v-bind:fields="fields"/>
    </div>
  </div>
</template>

<script>
import Banner from './components/Banner.vue'
import Fields from './components/Fields.vue'
import 'bootstrap/dist/css/bootstrap.min.css'

export default {
  name: 'app',
  components: {
    Banner,
    Fields
  },
  data() {
    return {
      fields: {
        creatorName: {
          creators: [''],
          label: 'Creator Name(s)',
          type: 'text',
        },
        objectType: {
          label: 'Object Type',
          type: 'select',
          choices: ['3d model', 'VR', '360 video'],
          value: ''
        },
        modelFileType: {
          label: 'File Type',
          type: 'select',
          choices: ['obj', 'glTF'],
          value: ''
        }
      }
    }
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
