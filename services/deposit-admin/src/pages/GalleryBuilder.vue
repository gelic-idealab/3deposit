<template>
    <div class="row">
        <div class="col-2">
        <input type="range" class="custom-range mb-3" min="1" max="5" v-model="column_count.columnCount">
            <div class="row mb-3">
                <p-button type="success" outline v-on:click.native="addFilter" class="mr-3">
                    <i class="ti ti-filter mr-1 mb-1"></i>
                    Add Filter
                </p-button>
                <p-button type="info" outline v-on:click.native="applyFilter">
                    <i class="ti ti-save mr-1"></i>
                    Apply
                </p-button>
            </div>
            <div class="row mb-2 col-10">
                    <div class="card text-center">
                    <div class="card-body">
                        <el-date-picker type="datetime" placeholder="Select Start Date" v-model="date_filter.value[0]">
                        </el-date-picker>
                        <el-date-picker type="datetime" placeholder="Select End Date" v-model="date_filter.value[1]">
                        </el-date-picker>
                    </div>
                </div>
            </div>
            <template v-for="(filter,index) in filters">
                <div :key="index" class="row mb-2">
                    <filter-key class="col-10" :key="index" :filter="filter">

                    </filter-key>
                    <p-button type="danger" outline icon v-on:click.native="removeFilter(index)" :key="index">
                        <i class="ti ti-trash"></i>
                    </p-button>
                </div>
            </template>
        </div>
        <div class="col-10">    
            <gallery :deposits="deposits" :column_count="column_count" :sortBy="sortBy" :filters="filters">

            </gallery>
        </div>
    </div>
</template>

<script>
import FilterKey from "./GalleryBuilder/FilterKey.vue";
import Gallery from "./GalleryBuilder/Gallery.vue";
import Button from "../components/Button.vue";

import axios from 'axios';
import querystring from 'querystring';
import {DatePicker, TimeSelect} from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css';
import lang from 'element-ui/lib/locale/lang/en'
import locale from 'element-ui/lib/locale'

locale.use(lang)

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
            date_filter: {
                key: 'deposit_date',
                op: 'Between',
                value: []
            },
            media_filter: {
                key: 'media_type',
                op: 'Equals',
                value: ['model', 'vr', 'video']
            }
        }
    },
    components: {
        FilterKey,
        Gallery,
        Button,
        [DatePicker.name]: DatePicker,
        [TimeSelect.name]: TimeSelect
    },
    created() {  
        axios.get("../api/gallery")
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
            this.filters.splice(index,1);
        },
        applyFilter() {
            let qs = JSON.stringify(this.filters);

            axios.get("../api/gallery", {params: {filters: qs}})
            .then(response => {
                this.deposits = response.data.deposits
                console.log(response.data)
            })  
        }
    }
}
</script>

<style>
</style>
