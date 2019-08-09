<template>
    <div class="card-columns">
        <div class="card" v-for="d in order(deposits)" :key="d.deposit_id">
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
            deposits: [],
            sortBy: {
                field: 'deposit_date',
                ascending: false
            }
        }
    },
    props: {
        column_count: Object,
        filters: Array
    },
    components: {
        GalleryCard
    },
    mounted() {
        let qs = JSON.stringify(this.filters);
        axios.get("../api/gallery", {params: {filters: qs}})
        .then(response => {
            this.deposits = response.data.deposits
        })
    },
    watch: {
        filters: function (newFilters, oldFilters) {
            let qs = JSON.stringify(newFilters);
            axios.get("../api/gallery", {params: {filters: qs}})
            .then(response => {
                this.deposits = response.data.deposits
            })
        }
    },
    methods: {
        order(deposits) {
             let sb = this.sortBy;
             if (sb.field==='deposit_date') {
                return deposits.slice().sort(function(a, b) {
                    var atime = a.deposit_date;
                    var btime = b.deposit_date;
                    if(sb.ascending===true) {
                        return atime - btime;
                    }
                    else {
                        return btime - atime; 
                    }
                });   
            }
        }
    }
}
</script>

