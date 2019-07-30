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
    mounted() {
        let query = JSON.parse(this.$route.query);
        this.filters = query.filters;
        this.sortBy = query.sortBy;
        this.column_count = query.column_count;
    }
}
</script>


<style>

</style>
