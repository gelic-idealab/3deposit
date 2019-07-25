<template>
    <div>
        <div class="card text-center">
            <div class="card-body">
                <select class="custom-select mb-3 row form-control form-control-sm" v-model="filter.key">
                    <template v-for="(key,index) in keys">
                        <option :value="key" :key="index">
                            {{ key }}
                        </option>
                    </template>
                </select>
                <select class="custom-select mb-3 row form-control form-control-sm" v-model="filter.op">
                    <template v-for="(op,index) in operators">
                        <option :value="op" :key="index">
                            {{ op }}
                        </option>
                    </template>
                </select>
                <template v-for="(v, index) in filter.value">                
                    <div class="mb-3 row input-group input-group-sm col col-offset-2" style="text-align: center" :key="index">
                        <input class="form-control form-control-sm" type="text" v-model="filter.value[index]">
                    </div>
                </template>
            </div>
        </div>
    </div>
</template>


<script>
import axios from 'axios'
import Button from '../../components/Button.vue'

export default {
    props: {
        filter: Object,
    },
    components: {
        Button,
    },
    data() {
        return {
            keys: [],
            operators: [],
        }
    },
    mounted() {
        axios.get("../api/metadata/keys")
        .then(response => this.keys = response.data.keys)
        this.operators = ['Equals','Contains','Greater Than', 'Less Than', 'Between', 'Excludes']
    },
    methods: {
        saveFilter() {
           
        },
    }
}

// $(function() {
//     $('#datetimepicker1').datetimepicker();
// });

</script>


<style>

    .fast .toggle-group { transition: left 0.1s; -webkit-transition: left 0.1s; }

</style>
