<template>
  <div align="center">
      <b-form-file v-if="file === 0"
        class="mb-3"
        v-model="file"
        id="add-file"
        :state="Boolean(file)"
        placeholder="Choose a file..."
        no-drop="true"
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
            header="Hash"
            style="max-width: 20rem;"
          >
            <b-card-text v-if="!hashed">
              Computing file checksum
              <b-spinner></b-spinner>
                {{ Math.round((currentChunk/chunks)*100) }}%
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
            header="Confirm"
            style="max-width: 20rem;"
          >
          <b-card-text>Server checksum matches</b-card-text>
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
      blobSlice: null,
      file: 0,
      fileReader: null,
      spark: null,
      hashing: false,
      hashed: false,
      paused: false,
      uploadPercentage: 0,
      chunkSize: 10*1024*1024, // 10MB
      maxFileSize: 1000*10*1024*1024, // 10GB
      chunks: 0,
      currentChunk: 1,
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
      this.file = 0;
      this.checksums = [];
      this.currentChunk = 1;
      this.chunks = 0;
      this.uploadPercentage = 0;
      this.hashed = false;
      this.hashing = false;
      this.r.cancel();
      axios.delete('../api/form/upload', {
        params: {
          deposit_id: this.id
          }
      })
      .then( () => {
        this.initR();
      });
    },
    loadNext() {
      var start = (this.currentChunk-1) * this.chunkSize,
          end = ((start + this.chunkSize) >= this.file.size) ? this.file.size : start + this.chunkSize;
      console.log('start', start, 'end', end)
      this.fileReader.readAsArrayBuffer(this.blobSlice.call(this.file, start, end));  
    },
    hashFile() {
      if (this.file) {
        var self = this;
        self.fileReader = new FileReader();
        self.spark = new SparkMD5.ArrayBuffer();
        self.hashing = true;
        self.chunks = Math.ceil(self.file.size / self.chunkSize);

        self.fileReader.onload = function (e) {
          console.log(self)
          self.spark.append(self.fileReader.result); // Append array buffer
          var hash = self.spark.end();
          self.checksums.push(hash);
          self.spark.reset();
          console.info('computed hash for chunk', self.currentChunk, 'of', self.chunks, hash);
          self.currentChunk++;

          if (self.currentChunk <= self.chunks) {
            console.log('loading next chunk')
            self.loadNext();
          } else {
            self.hashed = true;
            console.log('finished hashing');
          }
        };

        this.fileReader.onerror = function () {
          console.warn('oops, something went wrong.');
        };
        this.loadNext();
      }
    },
    handleFileAdd() {
      console.log('file added, hashing...')
      this.hashFile();
    },
    initR() {
      let comp = this;
      let r = new Resumable({ 
        target:'../api/form/upload',
        fileType: ['zip'],
        chunkSize: comp.chunkSize,
        maxFileSize: comp.maxFileSize,
        // xhrTimeout: 10000,
        testChunks: false,
        forceChunkSize: true,
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
    }
  },
  mounted() {
    this.blobSlice = File.prototype.slice || File.prototype.mozSlice || File.prototype.webkitSlice;
    this.initR();
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
  transition: all .3s cubic-bezier(1.0, 0.5, 0.8, 1.0);
}
.slide-fade-enter, .slide-fade-leave-to
/* .slide-fade-leave-active below version 2.1.8 */ {
  transform: translateX(10px);
  opacity: 0;
}

</style>