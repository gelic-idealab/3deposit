<template>
    <div class="card-columns" :style="column_count">
        <div class="card" v-for="d in order(this.deposits)" :key="d.deposit_id">
            <gallery-card 
                :deposit="d"
            >
            </gallery-card>
        </div>
    </div>
</template>

<script>
import GalleryCard from "./GalleryCard.vue";

export default {
    props: {
        deposits: Array,
        column_count: Object,
        sortBy: Object,
        filters: Array
    },
    components: {
        GalleryCard
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

