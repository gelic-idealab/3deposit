<template>
    <div>
        <input class="mr-3" type="text" v-model="deposit_form.form_id">Form ID
        <p-button @click.native.prevent="getForm">Load Form</p-button>
        <br>
        <div v-show="saveSuccess" class="alert alert-success">
            <button @click="saveSuccess = false" type="button" aria-hidden="true" class="close">×</button>
            <span>
                <b> Oh yeah - </b> form saved successfully</span>
        </div>

        <vue-json-editor v-model="deposit_form.content" :show-btns="true" @json-save="saveForm"></vue-json-editor>

    </div>
</template>

<script>
import axios from 'axios';
import vueJsonEditor from 'vue-json-editor'

export default {
    data() {
        return {
            deposit_form: {
                form_id: '',
                content: {}
            },
            saveSuccess: false
        }
    },
    components: {
        vueJsonEditor
    },
    mounted() {

    },
    methods: {
        getForm() {
            axios.get('../api/form', {params: {form_id: this.deposit_form.form_id}})
            .then(response => {
                if (response.data.form) {
                    this.deposit_form.content = response.data.form.content;
                    console.log(response.data.form.form_id, 'loaded')
                } else {
                    console.log('form does not exist')
                }
            })
        },
        saveForm() {
            axios.post('../api/form', this.deposit_form)
            .then(response => {
                if (response.status == 200) {
                    this.saveSuccess = true;
                }            
            })
        }
    }
};
</script>
<style>
</style>