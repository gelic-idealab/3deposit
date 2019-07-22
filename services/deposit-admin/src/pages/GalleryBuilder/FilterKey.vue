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
                <div class="mb-3 row input-group input-group-sm col col-offset-2" style="text-align: center">
                    <input class="form-control form-control-sm" type="text" v-model="filter.value">
                </div>
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
        Button
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
           
        }
    }
}
</script>


<style>

</style>
