<template>
  <div align="center">
      <b-form-file
        class="mb-3"
        v-model="file"
        id="add-file"
        :state="Boolean(file)"
        placeholder="Choose a file or drop it here..."
        drop-placeholder="Drop file here..."
        v-on:input="handleFileAdd"
        accept=".zip"
      ></b-form-file>

      <b-card-group deck>

        <transition name="slide-fade">
          <b-card v-if="hashing"
            border-variant="primary"
            header-bg-variant="primary"
            header-text-variant="white"
            align="center"
            class="text-center mb-5"
            header="Deposit Checksum"
            style="max-width: 20rem;"
          >
            <b-card-text v-if="!hashed">
              Computing file checksum
            </b-card-text>
            <b-card-text v-else-if="hashed">
              File checksum computed
            </b-card-text>
          </b-card>
        </transition>

        <transition name="slide-fade">
          <b-card v-if="hashed"
            border-variant="primary"
            header-bg-variant="primary"
            header-text-variant="white"
            align="center"
            class="text-center mb-5"
            header="Upload"
            style="max-width: 20rem;"
          >
            <b-card-text>
              <b-spinner v-if="uploadPercentage < 100"></b-spinner>
                {{ Math.round(uploadPercentage) }}%
              <!-- <b-button v-if="!paused" size="lg" variant="info" id="pause-upload-btn" @click="pauseUpload">Pause Upload</b-button>
              <b-button v-else-if="paused" size="lg" variant="primary" id="resume-upload-btn" @click="resumeUpload">Resume Upload</b-button> -->
            </b-card-text>
          </b-card>
        </transition>

        <transition name="slide-fade">
          <b-card v-if="uploadPercentage == 100 && hashed"
            border-variant="primary"
            header-bg-variant="primary"
            header-text-variant="white"
            align="center"
            class="text-center mb-5"
            header="Server checksum matches"
            style="max-width: 20rem;"
          >
          <b-button size="sm" variant="danger" id="uploaded-file-btn" @click="cancelUpload">
            Remove file and re-upload
          </b-button>
          </b-card>
        </transition>

      </b-card-group>

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
      hashing: false,
      hashed: false,
      paused: false,
      uploadPercentage: 0,
      chunkSize: 64*1024*1024, // 64MB
      maxFileSize: 1000*10*1024*1024, // 10GB
      checksums: [],
      r: {}
    }
  },
  methods: {
    pauseUpload() {
      this.r.pause();
      this.paused = true;
    },
    resumeUpload() {
      this.r.upload();
      this.paused = false;
      console.log('uploading...')
    },
    cancelUpload() {
      this.r.cancel();
      this.checksums = [];
      this.uploadPercentage = 0;
      this.hashed = false;
      this.hashing = false;
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
        checksums = this.checksums;
      var self = this;

      fileReader.onload = function (e) {
        // console.log('read chunk nr', currentChunk, 'of', chunks);
        spark.append(e.target.result);                   // Append array buffer

        if (currentChunk < chunks) {
          loadNext();
        } else {
          self.hashed = true;
          console.log('finished hashing');
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
    handleFileAdd() {
      this.hashFile();
      this.hashing = true;
    }
  },
  mounted() {
    let comp = this;
    let r = new Resumable({ 
            target:'../api/form/upload',
            fileType: ['zip'],
            chunkSize: comp.chunkSize,
            maxFileSize: comp.maxFileSize,
            // xhrTimeout: 10000,
            testChunks: false,
            query: {
              deposit_id: this.id,
              checksums: comp.checksums
            }
            });
    r.assignBrowse(document.getElementById('add-file'));
    r.on('progress', function () {
      comp.uploadPercentage = r.progress()*100
    });
    comp.r = r;
  },
  props: {
    id: String
  },
  watch: {
    hashed: function () {
      if (this.hashed) {
        this.resumeUpload();
      }
    },
    uploadPercentage: function () {
      if (this.uploadPercentage == 100) {
        this.$parent.finished_uploading = true;
      }
    }
  }
}
</script>

<style scoped>
.slide-fade-enter-active {
  transition: all .3s ease;
}
.slide-fade-leave-active {
  transition: all .8s cubic-bezier(1.0, 0.5, 0.8, 1.0);
}
.slide-fade-enter, .slide-fade-leave-to
/* .slide-fade-leave-active below version 2.1.8 */ {
  transform: translateX(10px);
  opacity: 0;
}

</style>