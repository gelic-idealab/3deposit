<template>
    <div>
        <div class="card-deck">
            <div class="card" v-for="(d, index) in this.deposits" :key="index">
                <gallery-card 
                    :deposit="d"
                >
                </gallery-card>
            </div>
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
    created() {  
        axios.get("http://localhost:8080/deposits")
        .then(response => this.deposits = response.data.deposits)
    }
}
</script>