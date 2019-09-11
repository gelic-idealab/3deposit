<template>
    <div>
        <vue-json-editor v-model="deposit_form.content" :show-btns="true" @json-save="saveForm"></vue-json-editor>
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
                form_id: 'deposit_form',
                content: {}
            }
        }
    },
    components: {
        VueJsonPretty,
        vueJsonEditor
    },
    mounted() {
        axios.get('../api/form', {params: {form_id: this.deposit_form.form_id}})
        .then(response => {
            this.deposit_form.content = response.data.form.content;
        })
    },
    methods: {
        saveForm() {
            axios.post('../api/form', this.deposit_form)
            .then(response => {
                console.log(response.data)
            })
        }
    }
};
</script>
<style>
</style>