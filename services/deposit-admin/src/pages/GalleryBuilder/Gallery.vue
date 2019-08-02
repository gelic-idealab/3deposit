<template>
    <div class="card-columns">
        <div class="card" v-for="d in deposits" :key="d.deposit_id">
            <gallery-card 
                :deposit="d"
            >
            </gallery-card>
        </div>
    </div>
</template>

<script>
import axios from 'axios';
import querystring from 'querystring';

import GalleryCard from "./GalleryCard.vue";

export default {
    data () {
        return {
            deposits: []
        }
    },
    props: {
        column_count: Object,
        sortBy: Object,
        filters: Array
    },
    components: {
        GalleryCard
    },
    mounted() {
        let qs = JSON.stringify(this.filters);
        console.log("Mounted",qs)

        axios.get("../api/gallery", {params: {filters: qs}})
        .then(response => {
            this.deposits = response.data.deposits
        })
    },
    watch: {
        filters: function (newFilters, oldFilters) {
            console.log(newFilters, oldFilters);
            let qs = JSON.stringify(newFilters);
            axios.get("../api/gallery", {params: {filters: qs}})
            .then(response => {
                this.deposits = response.data.deposits
            })
        }
    },
    methods: {
        // order(deposits) {
        //      let sb = this.sortBy;
        //      if (sb.field==='deposit_date') {
        //         return deposits.slice().sort(function(a, b) {
        //             var atime = new Date(a.deposit_date);
        //             var btime = new Date(b.deposit_date);
        //             if(sb.ascending===true) {
        //                 return atime.getTime() - btime.getTime();
        //             }
        //             else {
        //                 return btime.getTime() - atime.getTime(); 
        //             }
        //         });   
        //     }
        // }
    }
}
</script>

