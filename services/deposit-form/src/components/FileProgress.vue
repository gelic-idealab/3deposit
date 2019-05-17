<template>
  <div class="container sticky-top" style="background-color: white">
    <div class="large-12 medium-12 small-12 cell">
      <!-- <label>File
        <input type="file" id="file" ref="file" v-on:change="handleFileUpload()"/>
      </label> -->
        <div class="custom-file">
          <input type="file" class="custom-file-input" id="file" ref="file" v-on:change="handleFileUpload()" required>
          <label class="custom-file-label" for="file">Choose file...</label>
          <div class="invalid-feedback">Example invalid custom file feedback</div>
        </div>
      <br>
      <div class="progress mt-3 mb-3">
        <div class="progress-bar" role="progressbar" :style="{width: uploadPercentage+'%'}" aria-valuemin="0" aria-valuemax="100"></div>
      </div>
      <!-- <progress max="100" :value.prop="uploadPercentage"></progress> -->
      <br>
      <!-- <button v-on:click="submitFile()">Submit</button> -->
    </div>
  </div>
</template>

<script>
  import axios from 'axios'
  import CryptoJS from 'crypto-js'

export default {
  data(){
    return {
      file: '',
      uploadPercentage: 0,
      id: this.$parent.id,
      checksum: this.$parent.checksum

    }
  },
  methods: {
    hashFile(file, callback) {
      var fileReader = new FileReader();
      fileReader.onload = function() {
          var buff = fileReader.result;
          var md5 = CryptoJS.MD5(buff).toString();
          callback(md5);
      };
      fileReader.readAsArrayBuffer(file)
    },
    updateHash(md5) {
      this.checksum = md5
    },
    handleFileUpload() {
      this.file = this.$refs.file.files[0];
      this.hashFile(this.file, this.updateHash)
      this.submitFile();
    },
    submitFile() {
      let formData = new FormData();
      formData.append('id', this.id);
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

