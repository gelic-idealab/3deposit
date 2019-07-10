<template>
    <div>
        <div class="row">
            <div class ="col">
                <div class="card mb-3 mr-9">
                    <div class="embed-responsive embed-responsive-16by9">
                        <embed-card :location="deposit.location" class="embed-responsive-item"></embed-card>
                    </div>
                    <div class="card-body">
                        <h5 class="card-title">{{ deposit.deposit_id }}</h5>
                        <!-- <p class="card-text">{{ deposit_metadata }}</p> -->
                        <!-- <p class="card-text">{{ publish_metadata }}</p> -->
                        <p class="card-text"><small class="text-muted">{{ deposit.deposit_date }}</small></p>
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
                    <h5 class="card-header">User Metadata</h5>
                    <div class="card-body">
                        <vue-json-pretty
                            :data="deposit_metadata">
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
            deposit: {},
            deposit_metadata: {},
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
        axios.get("http://localhost:8080/metadata", {params: {deposit_id: this.id}})
        .then(response => (this.deposit_metadata = response.data.deposit_metadata))
        .then(response => {
            axios.get("http://localhost:8080/deposits", {params: {id: this.id}})
            .then(response => (this.deposit = response.data))
            .then(response => {
                axios.get("http://localhost:8080/publications", {params: {resource_id: this.deposit.resource_id, media_type: this.deposit_metadata.media_type}})
                .then(response => (this.publish_metadata = response.data))
            })     
            .then(console.log(this.deposit.resource_id))
        })
    }
};
</script>
<style>
</style>