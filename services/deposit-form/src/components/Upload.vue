<template>
  <div class="container sticky-top" style="background-color: white">
    <div class="large-12 medium-12 small-12 cell">

        <button type="button" class="btn btn-primary m-3" aria-label="Add file" id="add-file-btn">
            <span class="glyphicon glyphicon-plus" aria-hidden="true"></span> Add file
        </button>
          <!-- <input type="file" class="custom-file-input" id="file" ref="file" v-on:change="chunkUpload()" required>
          <label class="custom-file-label" for="file">Choose file...</label>
          <div class="invalid-feedback">Example invalid custom file feedback</div> -->
        <!-- </div> -->
      <br>
      <div class="progress mt-3 mb-3">
        <div class="progress-bar" role="progressbar" :style="{width: uploadPercentage+'%'}" aria-valuemin="0" aria-valuemax="100"></div>
      </div>
      <br>
    </div>
  </div>
</template>

<script>
//   import axios from 'axios'
//   import CryptoJS from 'crypto-js'
import Resumable from 'resumablejs'


export default {
  data(){
    return {
      uploadPercentage: 0,
      checksum: ''
    }
  },
  mounted () {
    let r = new Resumable({ 
            target:'https://a84503bf-79a4-421a-81bc-20b00eaf5244.mock.pstmn.io/upload',
            chunkSize: 10*1024*1024, // 10MB
            uploadMethod: 'POST',
            maxFileSize: 1000*10*1024*1024 // 10GB
            });
    r.assignBrowse(document.getElementById('add-file-btn'));
    r.on('fileAdded', function () {
        r.upload();
        console.log(r)
        r.on('progress', function() {
            console.log(r.progress()*100)
            })
    })
  },
  props: {
    id: String
  },
  methods: {
    }
}
</script>