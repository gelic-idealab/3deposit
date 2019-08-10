<template>
    <div>
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
                                <p-button type="danger" outline v-on:click.native="deleteDeposit" class="btn" style="width: 20%">
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
            id: ''
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
            axios.delete("../../api/publications", {params: {resource_id: this.deposit.resource_id, media_type: this.deposit.deposit_metadata.media_type}})
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
        deleteDeposit() {
            axios({
                url: "../../api/store/objects",
                method: 'DELETE',
                params: {deposit_id: this.id}
            })
            .then((response) => {
                console.log(response.data)
            });
        }
    }
}
</script>


<style>

</style>