<template>
    <gallery :filters="filters"></gallery>    
</template>


<script>
import Gallery from "./GalleryBuilder/Gallery.vue";

export default {
    data() {
        return {
            filters: [],
            sortBy: {},
            column_count : {}
        }
    },
    components: {
        Gallery
    },
    created() {
        this.filters = JSON.parse(this.$route.query.filters);
        // this.sortBy = query.sortBy;
        // this.column_count = query.column_count;
        // console.log("FILTERS:",this.filters);
    }
}
</script>


<style>

</style>
