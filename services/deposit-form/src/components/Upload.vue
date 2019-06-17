<template>
  <div class="container sticky-top" style="background-color: white">
    <div class="large-12 medium-12 small-12 cell">

        <button type="button" class="btn btn-primary m-3" aria-label="Add file" id="add-file-btn">
            <span class="glyphicon glyphicon-plus" aria-hidden="true"></span> Add file
        </button>
  
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
    let comp = this
    let r = new Resumable({ 
            target:'http://gateway.docker.localhost/deposit/upload',
            chunkSize: 10*1024*1024, // 10MB
            maxFileSize: 1000*10*1024*1024, // 10GB
            testChunks: false,
            query: {
              deposit_id: this.id
            }
            });
    r.assignBrowse(document.getElementById('add-file-btn'));
    r.on('fileAdded', function () {
        r.upload( function () {
          console.log('uploading chunk')
        });
        r.on('progress', function () {
          comp.uploadPercentage = r.progress()*100
          });
    });
  },
  props: {
    id: String
  },
  methods: {
    }
}
</script>