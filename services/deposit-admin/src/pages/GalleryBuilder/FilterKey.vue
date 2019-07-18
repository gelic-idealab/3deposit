<template>
    <div>
        <div class="row">
            <select class="custom-select col-4 mr-3" v-model="filter.key">
                <template v-for="(key,index) in keys">
                    <option :value="key" :key="index">
                        {{ key }}
                    </option>
                </template>
            </select>
            <select class="custom-select col-4 mr-3" v-model="filter.op">
                <template v-for="(op,index) in operators">
                    <option :value="op" :key="index">
                        {{ op }}
                    </option>
                </template>
            </select>
            <input class="mr-3" type="text" v-model="filter.value">
        </div>
    </div>
</template>


<script>
import axios from 'axios'
import Button from '../../components/Button.vue'

export default {
    props: {
        filter: Array,
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
            this.$emit('addFilter', temp);
            console.log("save_filter",this.filter)
        }
    }
}
</script>


<style>

</style>
