<template>
  <div class="container">
    <div class="large-12 medium-12 small-12 cell">
      <label>File
        <input type="file" id="file" ref="file" v-on:change="handleFileUpload()"/>
      </label>
      <br>
      <progress max="100" :value.prop="uploadPercentage"></progress>
      <br>
      <!-- <button v-on:click="submitFile()">Submit</button> -->
    </div>
  </div>
</template>

<script>
  import axios from 'axios'

export default {
  data(){
    return {
      file: '',
      uploadPercentage: 0,
      id: this.$parent.id
    }
  },
  methods: {
    handleFileUpload() {
      this.file = this.$refs.file.files[0];
      this.submitFile();
    },
    submitFile() {
      let formData = new FormData();
      formData.append('id', this.data.id)
      formData.append('file', this.file);
      axios.post( 'https://a84503bf-79a4-421a-81bc-20b00eaf5244.mock.pstmn.io/upload',
        formData,
        {
          headers: {
              'Content-Type': 'multipart/form-data'
          },
          onUploadProgress: function( progressEvent ) {
            this.uploadPercentage = parseInt( Math.round( ( progressEvent.loaded * 100 ) / progressEvent.total ) );
          }.bind(this)
        } 
      ).then(function(){
        // console.log('SUCCESS!!');
      })
      .catch(function(){
       // console.log('FAILURE!!');
      });
    },
  }
}

</script>

