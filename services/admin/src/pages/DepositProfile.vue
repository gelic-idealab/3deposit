<template>
    <div>

        <div v-if="confirmDelete">
            <transition name="modal">
            <div class="modal-mask">
            <div class="modal-wrapper">
                <div class="modal-container text-center">

                <div class="modal-header text-center">
                    <slot name="header">
                    Confirm Delete?
                    </slot>
                </div>

                <!-- <div class="modal-body">
                    <p class="my-4">Are you sure you want to delete {{ id }}?</p>
                </div> -->

                <div class="modal-footer">
                    <p-button type="danger" v-on:click.native="deleteDeposit">Yes</p-button>
                    <p-button type="primary" v-on:click.native="confirmDeletefunc">Cancel</p-button>
                </div>
                </div>
            </div>
            </div>
            </transition>
        </div>

        <div class="row">
            <div class ="col">
             
                <div class="card mb-3 mr-9">
                    <div class="embed-responsive embed-responsive-16by9">
                        <embed-card :location="deposit.deposit_metadata.location" class="embed-responsive-item"></embed-card>
                    </div>
                    <div class="card-body">
                        <h5 class="card-title">{{ deposit.deposit_id }}</h5>
                        <!-- <p class="card-text">{{ deposit_metadata }}</p> -->
                        <!-- <p class="card-text">{{ publish_metadata }}</p> -->
                        <p class="card-text"><small class="text-muted">{{ pretty_date }}</small></p>
                    </div>
                </div>
                <div class="card mb-3 mr-9">
                    <div class="card-body">
                        <div class="row">
                            <div class="container d-flex justify-content-around">
                                <p-button type="success" outline v-on:click.native="downloadDeposit" class="btn" style="width: 20%">
                                    <i class="ti ti-download mr-1"></i>
                                    Download
                                </p-button>
                                <p-button type="info" outline v-on:click.native="republishDeposit" class="btn" style="width: 20%">
                                    <i class="ti ti-reload mr-1"></i>
                                    Republish
                                </p-button>
                                <p-button type="warning" outline v-on:click.native="unpublishDeposit" class="btn" style="width: 20%">
                                    <i class="ti ti-close mr-1"></i>
                                    Unpublish
                                </p-button>
                                <p-button type="danger" outline v-on:click.native="confirmDeletefunc" class="btn" style="width: 20%">
                                    <i class="ti ti-trash mr-1"></i>
                                    Delete
                                </p-button>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="card">
                    <h5 class="card-header">Publication Metadata</h5>
                    <div class="card-body">
                        <vue-json-pretty
                            :data="publish_metadata"
                            :deep=4>
                        </vue-json-pretty>
                    </div>
                </div>
            </div>
            <div class="col">
                <div class="card">
                    <h5 class="card-header">Metadata</h5>
                    <div class="card-body">
                        <vue-json-pretty
                            :data="deposit">
                        </vue-json-pretty>
                    </div>
                </div>
            </div>
        </div>        
    </div>
</template>


<script>
import axios from 'axios';
import EmbedCard from "./DepositProfile/EmbedCard.vue";
import MetadataJson from "./DepositProfile/MetadataJson.vue";
import VueJsonPretty from 'vue-json-pretty'

export default {
    data() {
        return{
            pretty_date: '',
            deposit: {
                deposit_metadata: {},
                deposit_date: ''
            },
            publish_metadata: {},
            id: '',
            confirmDelete: false
        }
    },
    components: {
        EmbedCard,
        MetadataJson,
        VueJsonPretty
    },
    mounted() {
        this.id = this.$route.params.id;
        console.log(this.id);
        axios.get("../../api/metadata", {params: {deposit_id: this.id}})
        .then(response => {
            this.deposit = response.data;
            this.pretty_date = new Date(response.data.deposit_date * 1000);
            axios.get("../../api/publications", {
                params: {
                    resource_id: response.data.deposit_metadata.resource_id, 
                    media_type: response.data.deposit_metadata.media_type
                }
            })
            .then(response => {(this.publish_metadata = response.data)})
        })
    },
    methods: {
        unpublishDeposit() {
            axios.delete("../../api/publications", {
                params: {
                    resource_id: this.deposit.deposit_metadata.resource_id, 
                    media_type: this.deposit.deposit_metadata.media_type
                }
            })
            .then(response => {
                if(response.status === 200) {
                    axios.patch("../../api/metadata", {location: 'None'}, {params: {deposit_id: this.id}})
                }
            })
        },
        downloadDeposit() {
            axios({
                url: "../../api/store/objects",
                method: 'GET',
                params: {deposit_id: this.id},
                responseType: 'blob'
            })
            .then((response) => {
                const url = window.URL.createObjectURL(new Blob([response.data]));
                const link = document.createElement('a');
                link.href = url;
                link.setAttribute('download', this.id+'.zip'); //or any other extension
                document.body.appendChild(link);
                link.click();
            });
        },
        confirmDeletefunc() {
            this.confirmDelete = !this.confirmDelete;
        },
        deleteDeposit() {
            axios({
                url: "../../api/store/objects",
                method: 'DELETE',
                params: {deposit_id: this.id}
            })
            .then((response) => {
                console.log(response.data)
                this.confirmDeletefunc();
            });
        }
    }
}
</script>


<style>
.modal-mask {
  position: fixed;
  z-index: 9998;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, .5);
  display: table;
  transition: opacity .3s ease;
}

.modal-wrapper {
  display: table-cell;
  vertical-align: middle;
}

.modal-container {
  width: 300px;
  margin: 0px auto;
  padding: 20px 30px;
  background-color: #fff;
  border-radius: 2px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, .33);
  transition: all .3s ease;
  font-family: Helvetica, Arial, sans-serif;
}

.modal-header h3 {
  margin-top: 0;
  color: #42b983;
}

.modal-body {
  margin: 20px 0;
}


/*
 * The following styles are auto-applied to elements with
 * transition="modal" when their visibility is toggled
 * by Vue.js.
 *
 * You can easily play with the modal transition by editing
 * these styles.
 */

.modal-enter {
  opacity: 0;
}

.modal-leave-active {
  opacity: 0;
}

.modal-enter .modal-container,
.modal-leave-active .modal-container {
  -webkit-transform: scale(1.1);
  transform: scale(1.1);
}
</style>