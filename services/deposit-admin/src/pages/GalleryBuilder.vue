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
                <p-button type="info" outline v-on:click.native="generateEmbed">
                    <i class="ti ti-sharethis mr-1"></i>
                    Embed
                </p-button>
            </div>
            <div class="row mb-2">
                <div class=" col-10">
                    <div class="card text-center">
                        <div class="card-body col-12">
                            <el-date-picker class="row" type="datetime" placeholder="Select Start Date" v-model="date_filter.value[0][0]">
                            </el-date-picker>
                            <el-date-picker class="row" type="datetime" placeholder="Select End Date" v-model="date_filter.value[0][1]">
                            </el-date-picker>
                        </div>
                    </div>
                </div>
            </div>
            <div class="row mb-2">
                <div class=" col-10">
                    <div class="card">
                        <div class="card-body col-12">
                            <template v-for="option in media_filter.options">
                                <div class="form-check" :key="option.value">
                                    <label class="form-check-label">
                                        <input class="form-check-input" :id="option.value" :value="option.value" v-model="media_filter.value" type="checkbox" checked>
                                        {{ option.label }}
                                        <span class="check"></span>
                                    </label>
                                </div>
                            </template>
                        </div>
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
            <gallery :column_count="column_count" :sortBy="sortBy" :filters="all_filters">

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
            all_filters: [],
            column_count: {
                columnCount: 3
            },
            date_filter: {
                key: 'deposit_date',
                op: 'Between',
                value: [[]]
            },
            media_filter: {
                key: 'media_type',
                op: 'Equals',
                value: ['model', 'vr', 'video'],
                options: [
                    {
                        label: 'Model',
                        value: 'model'
                    },
                    {
                        label: 'VR App',
                        value: 'vr'
                    },
                    {
                        label: '360 Video',
                        value: 'video'
                    }
                ]
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
    //     axios.get("../api/gallery")
    //     .then(response => {
    //         this.deposits = response.data.deposits
    //     },
    //     error => {
    //         if (error.response.status === 401) {
    //             window.location.href = '../api/login';
    //     }
    // });
    },
    methods: {
        addFilter() {
            this.filters.push({
                key: '',
                op: '',
                value: ['']
            })
        },
        removeFilter(index) {
            this.filters.splice(index,1);
        },
        applyFilter() {
            // let all_filters
            if(!(this.date_filter.value[0][0]==null || this.date_filter.value[0][1]==null)) {
                let formatted_date_filter = {};
                formatted_date_filter.key = this.date_filter.key
                formatted_date_filter.op = this.date_filter.op
                formatted_date_filter.value = [[]]

                this.date_filter.value.forEach(function(value, index) { 
                    formatted_date_filter.value[index][0] = Date.parse(value[0])/1000
                    formatted_date_filter.value[index][1] = Date.parse(value[1])/1000
                })

                this.all_filters = this.filters.concat([this.media_filter, formatted_date_filter])
            }
            else {
                this.all_filters = this.filters.concat([this.media_filter])
            }
            // let qs = JSON.stringify(all_filters);
            // axios.get("../api/gallery", {params: {filters: qs}})
            // .then(response => {
            //     this.deposits = response.data.deposits
            // })  
        },
        generateEmbed() {
            const location = window.location.href;
            location.replace("gallery-builder", "public/gallery?")
            let qs = JSON.stringify(this.all_filters)
            let embed = location.concat(qs)
            console.log(embed)
        }
    }
}
</script>


<style>
</style>
