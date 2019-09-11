<template>
    <div>
      
    </div>
</template>

<script>
import axios from 'axios';
import VueJsonPretty from 'vue-json-pretty';


export default {
    data() {
        return{
            deposit_form: {}
        }
    },
    props: {
        form: Object
    },
    components: {

    },
    mounted() {
        this.deposit_form = this.form;
        
    }
};
</script>
<style>
</style>