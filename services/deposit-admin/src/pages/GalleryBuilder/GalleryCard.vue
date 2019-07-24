<template>
    <div>
        <template v-if="deposit.deposit_metadata.media_type==='vr'">
            <a :href="location">
                <img class="card-img-top" src="../../assets/img/vr.svg"/>
            </a>
        </template>
        <template v-else-if="deposit.deposit_metadata.media_type==='model'">
            <a :href="location">
                <div class="embed-responsive embed-responsive-16by9">
                    <!-- <embed class="embed-responsive-item" :src="publish_metadata.thumbnails.images[2].url"/> -->
                    <embed class="embed-responsive-item" :src="location"/>
                </div>
            </a>
        </template>
        <template v-else-if="deposit.deposit_metadata.media_type==='video'">
            <a :href="location">
                <div class="embed-responsive embed-responsive-16by9">
                    <embed class="embed-responsive-item" :src="location"/>
                </div>
            </a>
        </template>
        <div class="card-body">
            <h5 class="card-title mb-3">{{ deposit.deposit_metadata.object_title }}</h5>
            <p class="card-text">{{ deposit.deposit_metadata.description }}</p>
        </div>
        <div class="card-footer text-muted">{{ deposit_date.substring(0, deposit_date.indexOf('.')) }}</div>
    </div>
</template>
<script>

import VueJsonPretty from 'vue-json-pretty'
import axios from 'axios'

export default {
    data() {
        return {
            resource_id: '',
            location: '',
            deposit_date: '',
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
        axios.get("../api/deposits", {params: {deposit_id: this.deposit.deposit_id}})
        .then(response => {
            this.resource_id = response.data.resource_id;
            this.location = response.data.location;
            this.deposit_date = response.data.deposit_date;
        })
        .then(() => {
            axios.get("../api/publications", {params: {resource_id: this.resource_id, media_type: this.deposit.deposit_metadata.media_type}})
            .then(response => this.publish_metadata = response.data);
        })

    }
}
</script>
<style>
</style>
