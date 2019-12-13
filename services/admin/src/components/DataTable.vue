<template>
    <data-tables :data="data" :tableProps="tableProps" :filters="customFilters">DataTable</data-tables>
</template>

<script>
import { DataTables } from 'vue-data-tables';

export default {
    components: {
        DataTables
    },
    props: {
        data: Array
    },
    data () {
        return {
            tableProps: null,
            customFilters: null
        }
    }
}

</script>

<style>

</style>