<template>
    <div>
        <div class="card" v-for="(d, index) in this.deposits" :key="index">
            <gallery-card :deposit="d">

            </gallery-card>
        </div>
    </div>
</template>

<script>
import axios from 'axios';
import GalleryCard from "./GalleryBuilder/GalleryCard.vue";

export default {
    name: "gallery-builder",
    data() {
        return{
            deposits: [],
        }
    },
    components: {
        GalleryCard
    },
    mounted() {
            axios.get("http://localhost:8080/deposits")
            .then(response => {
                this.deposits = response.data.deposits;
                this.deposits.forEach(deposit => {
                    axios.get("http://localhost:8080/metadata", {params: {deposit_id: deposit.deposit_id}})
                    .then(response => deposit['deposit_metadata'] = response.data.deposit_metadata);
                    axios.get("http://localhost:8080/publications", {params: {resource_id: deposit.resource_id, media_type: deposit.media_type}})
                    .then(response => deposit['publish_metadata'] = response.data);
                })
            }
            )
    }
};
</script>