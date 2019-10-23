<template>
  <div align="center">

    <b-form-file
      v-model="file"
      id="add-file"
      :state="Boolean(file)"
      placeholder="Choose a file or drop it here..."
      drop-placeholder="Drop file here..."
      v-on:input="hashFile"
      accept=".zip"
      required="true"
    ></b-form-file>
    <br />

    <!-- <b-card
      class="text-center mb-5"
      header="Step 1: Upload"
      style="max-width: 20rem;"
    >
      <b-card-text>
        Select a .zip file to upload in the background while you complete the rest of the form. 
      </b-card-text>

    <b-button v-if="uploadPercentage == 0" size="lg" type="file" variant="primary" @change="hashFile">
      Add file
    </b-button>

    <template v-else-if="uploadPercentage < 100">
      <b-button size="lg" variant="primary" id="uploading-file-btn">
        <b-spinner></b-spinner>
          {{ Math.round(uploadPercentage) }}%
      </b-button>
      <b-button v-if="!paused" size="lg" variant="info" id="pause-upload-btn" @click="pauseUpload">Pause Upload</b-button>
      <b-button v-else-if="paused" size="lg" variant="primary" id="resume-upload-btn" @click="resumeUpload">Resume Upload</b-button>
      <b-button size="lg" variant="danger" id="cancel-upload-btn" @click="cancelUpload">X</b-button>
    </template>

    <b-button v-else-if="uploadPercentage == 100" size="lg" variant="warning" id="uploaded-file-btn" @click="cancelUpload">
      Upload successful - click to cancel and re-upload
    </b-button>
  </b-card> -->
    <!-- <div class="progress mt-3 mb-3">
      <div class="progress-bar" role="progressbar" :style="{width: uploadPercentage+'%'}" aria-valuemin="0" aria-valuemax="100"></div>
    </div> -->
    <!-- <br> -->
  </div>
</template>


<script>
import axios from 'axios'
import SparkMD5 from 'spark-md5'
import Resumable from 'resumablejs'


export default {
  data(){
    return {
      file: 0,
      paused: false,
      uploadPercentage: 0,
      chunkSize: 64*1024*1024, // 64MB
      maxFileSize: 1000*10*1024*1024, // 10GB
      checksums: [],
      r: {}
    }
  },
  methods: {
    pauseUpload () {
      this.r.pause();
      this.paused = true;
    },
    resumeUpload () {
      this.r.upload();
      this.paused = false;
    },
    cancelUpload () {
      this.r.cancel();
      axios.delete('../api/form/upload', {
        params: {
          deposit_id: this.id
          }
      });
    },
    hashFile() {
      var blobSlice = File.prototype.slice || File.prototype.mozSlice || File.prototype.webkitSlice,
        file = this.file,
        chunkSize = this.chunkSize,
        chunks = Math.ceil(file.size / chunkSize),
        currentChunk = 0,
        spark = new SparkMD5.ArrayBuffer(),
        fileReader = new FileReader(),
        checksums = this.checksums

      fileReader.onload = function (e) {
          console.log('read chunk nr', currentChunk, 'of', chunks);
          spark.append(e.target.result);                   // Append array buffer

          if (currentChunk < chunks) {
              loadNext();
          } else {
              console.log('finished loading');
          }
      };

      fileReader.onerror = function () {
          console.warn('oops, something went wrong.');
      };

      function loadNext() {
          var start = currentChunk * chunkSize,
              end = ((start + chunkSize) >= file.size) ? file.size : start + chunkSize;

          fileReader.readAsArrayBuffer(blobSlice.call(file, start, end));
          var hash = spark.end();
          checksums.push(hash);
          console.info('computed hash for chunk', currentChunk, hash);
          currentChunk++;

      }

      loadNext();
    },
    handleFileUpload() {
      this.hashFile();
      this.submitFile();
    }
  },
  mounted () {
    let comp = this;
    let r = new Resumable({ 
            target:'../api/form/upload',
            fileType: ['zip'],
            chunkSize: comp.chunkSize,
            maxFileSize: comp.maxFileSize,
            // xhrTimeout: 10000,
            testChunks: false,
            query: {
              deposit_id: this.id
              // checksum: comp.checksums[chunkNumber]
            }
            });
    r.assignBrowse(document.getElementById('add-file'));
    r.on('fileAdded', function () {
      r.on('progress', function () {
        comp.uploadPercentage = r.progress()*100
      });
    });
    comp.r = r;
  },
  props: {
    id: String
  },
  watch: {
    uploadPercentage: function () {
      if (this.uploadPercentage == 100) {
        this.$parent.finished_uploading = true;
      }
    }
  }
}
</script>

<style scoped>

</style>