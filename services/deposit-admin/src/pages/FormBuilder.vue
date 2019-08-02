<template>
    <div>
        <vue-json-editor v-model="deposit_form" :show-btns="true"></vue-json-editor>
      <!-- <vue-json-pretty 
        :data="deposit_form">
      </vue-json-pretty> -->
    </div>
</template>

<script>
import axios from 'axios';
import VueJsonPretty from 'vue-json-pretty';
import vueJsonEditor from 'vue-json-editor'

export default {
    data() {
        return {
            deposit_form: {
                content: {}
            }
        }
    },
    components: {
        VueJsonPretty,
        vueJsonEditor
    },
    mounted() {
        axios.get('../api/form')
        .then(response => {
            this.deposit_form = response.data.form.content;
        })
    }
};
</script>
<style>
</style>