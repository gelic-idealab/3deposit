<template>
    <div>
        <div class="card-columns" style="column-count: 5">
            <!-- <div class="col-lg-15"> -->
                <div class="card" v-for="(d, index) in order(this.deposits)" :key="index">
                    <gallery-card 
                        :deposit="d"
                    >
                    </gallery-card>
                </div>
            <!-- </div> -->
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
            sortBy: {
                field: 'deposit_date',
                ascending: false
            }
        }
    },
    components: {
        GalleryCard
    },
    created() {  
        axios.get("http://localhost:8080/deposits")
        .then(response => this.deposits = response.data.deposits)
    },
    methods: {
         order(deposits) {
             let sb = this.sortBy;
             if (sb.field==='deposit_date') {
                return deposits.slice().sort(function(a, b) {
                    var atime = new Date(a.deposit_date);
                    var btime = new Date(b.deposit_date);
                    if(sb.ascending===true) {
                        return atime.getTime() - btime.getTime();
                    }
                    else {
                        return btime.getTime() - atime.getTime(); 
                    }
                });   
            }
        }
    }
}
</script>

<style>
</style>
