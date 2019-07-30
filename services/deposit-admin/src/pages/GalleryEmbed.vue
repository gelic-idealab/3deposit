<template>
    <gallery :filters="filters"></gallery>    
</template>


<script>
import Gallery from "./GalleryBuilder/Gallery.vue";

export default {
    data() {
        return {
            filters: []
        }
    },
    components: {
        Gallery
    },
    mounted() {
        this.filters = JSON.parse(this.$route.query.filters);
    }
}
</script>


<style>

</style>
