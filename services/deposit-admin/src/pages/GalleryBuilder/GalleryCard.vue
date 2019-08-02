<template>
    <div>
        <template v-if="deposit.deposit_metadata.media_type==='vr'">
            <a :href="deposit.location" target="_blank">
                <img class="card-img-top" src="../../assets/img/vr.svg"/>
            </a>
        </template>
        <template v-else-if="deposit.deposit_metadata.media_type==='model'">
            <a :href="location">
                <div class="embed-responsive embed-responsive-16by9">
                    <!-- <embed class="embed-responsive-item" :src="publish_metadata.thumbnails.images[2].url"/> -->
                    <embed class="embed-responsive-item" :src="deposit.location"/>
                </div>
            </a>
        </template>
        <template v-else-if="deposit.deposit_metadata.media_type==='video'">
            <a :href="location">
                <div class="embed-responsive embed-responsive-16by9">
                    <embed class="embed-responsive-item" :src="deposit.location"/>
                </div>
            </a>
        </template>
        <div class="card-body">
            <h5 class="card-title mb-3">{{ deposit.deposit_metadata.object_title }}</h5>
            <p class="card-text">{{ deposit.deposit_metadata.description }}</p>
        </div>
        <div class="card-footer text-muted">{{ pretty_date }}</div>
    </div>
</template>


<script>

import VueJsonPretty from 'vue-json-pretty'
import axios from 'axios'

export default {
    data() {
        return {
            pretty_date: '',
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
        axios.get("../api/publications", {params: {resource_id: this.deposit.resource_id, media_type: this.deposit.deposit_metadata.media_type}})
        .then(response => this.publish_metadata = response.data);
        this.pretty_date = new Date(this.deposit.deposit_date * 1000)
    }
}
</script>


<style>

</style>
