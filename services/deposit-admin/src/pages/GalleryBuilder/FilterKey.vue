<template>
    <div>
        <div class="row">
            <select class="custom-select col-4 mr-3" v-model="filter.key">
                <template v-for="key in keys">
                    <option :value="key" :key="key">
                        {{ key }}
                    </option>
                </template>
            </select>
            <select class="custom-select col-4 mr-3" v-model="filter.op">
                <template v-for="op in operators">
                    <option :value="op" :key="op">
                        {{ op }}
                    </option>
                </template>
            </select>
            <input class="mr-3" type="text" v-model="filter.value">
            <Button class="btn-round" v-on:click.native="saveFilter">Save</Button>
        </div>
    </div>
</template>


<script>
import axios from 'axios'
import Button from '../../components/Button.vue'

export default {
    components: {
        Button
    },
    data() {
        return {
            keys: [],
            operators: [],
            filter: {
                key: '',
                op: '',
                value: ''
            }
        }
    },
    mounted() {
        axios.get("http://localhost:8080/metadata/keys")
        .then(response => this.keys = response.data.keys)
        this.operators = ['Equals','Contains','Greater Than', 'Less Than', 'Between', 'Excludes']
    },
    methods: {
        saveFilter() {
            this.$emit('addFilter', this.filter);
            console.log("save_filter",this.filter)
        }
    }
}
</script>


<style>

</style>
