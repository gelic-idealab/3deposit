<template>
  <div>
    <b-button v-if="uploadPercentage == 0" size="lg" variant="primary" id="add-file-btn">
      Add file
    </b-button>
    <template v-else-if="uploadPercentage < 100">
      <b-button size="lg" variant="primary" id="uploading-file-btn">
        <b-spinner></b-spinner>
          {{ Math.round(uploadPercentage) }}%
      </b-button>
      <b-button size="lg" variant="info" id="pause-upload-btn" @click="pauseUpload">Pause Upload</b-button>
      <b-button size="lg" variant="danger" id="cancel-upload-btn" @click="cancelUpload">Cancel Upload</b-button>
    </template>
    <b-button v-else-if="uploadPercentage == 100" size="lg" variant="success" id="uploaded-file-btn">
      Upload Successful
    </b-button>

    <br>
    <!-- <div class="progress mt-3 mb-3">
      <div class="progress-bar" role="progressbar" :style="{width: uploadPercentage+'%'}" aria-valuemin="0" aria-valuemax="100"></div>
    </div> -->
    <!-- <br> -->
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
      checksum: '',
      r: {}
    }
  },
  methods: {
    pauseUpload () {
      this.r.pause();
    },
    cancelUpload () {
      this.r.cancel();
    }
  },
  mounted () {
    let comp = this;
    let r = new Resumable({ 
            target:'../api/form/upload',
            fileType: ['zip'],
            chunkSize: 64*1024*1024, // 64MB
            maxFileSize: 1000*10*1024*1024, // 10GB
            testChunks: false,
            query: {
              deposit_id: this.id
            }
            });
    r.assignBrowse(document.getElementById('add-file-btn'));
    r.on('fileAdded', function () {
      r.upload( function () {
      });
      r.on('progress', function () {
        comp.uploadPercentage = r.progress()*100
      });
    });
    comp.r = r;
  },
  props: {
    id: String
  }
}
</script>