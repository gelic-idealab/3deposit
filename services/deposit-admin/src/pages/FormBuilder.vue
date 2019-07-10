<template>
    <div>
      <vue-json-pretty 
        :data="deposit_form">
      </vue-json-pretty>
    </div>
</template>

<script>
import axios from 'axios';
import VueJsonPretty from 'vue-json-pretty';

export default {
    data() {
        return {
            deposit_form: {}
        }
    },
    components: {
        VueJsonPretty
    },
    mounted() {
        axios.get('http://localhost:8080/form')
        .then(response => {
            this.deposit_form = response.data.form.content;
        })
    }
};
</script>
<style>
</style>