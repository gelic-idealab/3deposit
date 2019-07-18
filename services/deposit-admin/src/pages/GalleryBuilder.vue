<template>
    <div>
        <gallery :deposits="deposits" :column_count="column_count" :sortBy="sortBy" :filters="filters">

        </gallery>
        <template v-for="(filter,index) in filters">
            <div :key="index" class="row mb-2">
                <filter-key class="col-10" :key="index" :filter="filter">

                </filter-key>
                <p-button type="danger" outline icon v-on:click.native="removeFilter(index)" :key="index">
                    <i class="ti ti-trash"></i>
                </p-button>
            </div>
        </template>
        <p-button type="success" outline icon v-on:click.native="addFilter">
            <i class="ti ti-filter"></i>
        </p-button>
        <input type="range" class="custom-range" min="1" max="5" v-model="column_count.columnCount">

    </div>
</template>

<script>
import axios from 'axios';
import FilterKey from "./GalleryBuilder/FilterKey.vue"
import Gallery from "./GalleryBuilder/Gallery.vue"
import Button from "../components/Button.vue"

export default {
    name: "gallery-builder",
    data() {
        return{
            deposits: [],
            sortBy: {
                field: 'deposit_date',
                ascending: false
            },
            filters: [],
            column_count: {
                columnCount: 5
            },
        }
    },
    components: {
        FilterKey,
        Gallery,
        Button
    },
    created() {  
        axios.get("../api/deposits")
        .then(response => this.deposits = response.data.deposits)
    },
    methods: {
        addFilter() {
            this.filters.push({
                key: '',
                op: '',
                value: ''
            })
        },
        removeFilter(index) {
            this.filters.splice(index,1)
        }
    }
}
</script>

<style>
</style>
