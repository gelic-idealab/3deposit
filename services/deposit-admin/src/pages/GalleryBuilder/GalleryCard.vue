<template>
    <div>
        <template v-if="deposit.media_type==='vr'">
            <a :href="deposit.location">
                <img class="card-img-top" src="../../assets/img/vr.svg"/>
            </a>
        </template>
        <template v-else-if="deposit.media_type==='model'">
            <a :href="deposit.location">
                <div class="embed-responsive embed-responsive-16by9">
                    <embed class="embed-responsive-item" :src="publish_metadata.thumbnails.images[2].url"/>
                </div>
            </a>
        </template>
        <div class="card-body">
            <h5 class="card-title mb-3">{{ deposit_metadata['Object Title'] }}</h5>
            <p class="card-text">{{ deposit_metadata.description }}</p>
        </div>
        <div class="card-footer text-muted">{{ deposit.deposit_date.substring(0, deposit.deposit_date.indexOf('.')) }}</div>
    </div>
</template>
<script>

import VueJsonPretty from 'vue-json-pretty'
import axios from 'axios'

export default {
    data() {
        return {
            deposit_metadata: {},
            publish_metadata: {
                thumbnails: {
                    images: [{
                        url: ''
                    },
                    {
                        url: ''
                    },
                    {
                        url: ''
                    }]
                }
            },
        }
    },
    props: {
        deposit: Object,
    },
    mounted() {
        axios.get("http://localhost:8080/metadata", {params: {deposit_id: this.deposit.deposit_id}})
        .then(response => this.deposit_metadata = response.data.deposit_metadata);
        axios.get("http://localhost:8080/publications", {params: {resource_id: this.deposit.resource_id, media_type: this.deposit.media_type}})
        .then(response => this.publish_metadata = response.data);
    }
}
</script>
<style>
</style>
