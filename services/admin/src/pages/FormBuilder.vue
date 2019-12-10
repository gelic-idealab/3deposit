<template>
    <div>
        <b-form inline>
            <b-input
                id="inline-form-input-name"
                class="mb-2 mr-sm-2 mb-sm-0"
                label="Form ID"
                placeholder="Form ID"
                v-model="deposit_form.content.id"
            ></b-input>
            <b-button variant="primary" @click="getForm">Load</b-button>
        </b-form>

        
        <!-- Form ID<input class="ml-3 mr-3 mb-3" type="text" v-model="deposit_form.form_id">
        <p-button @click.native.prevent="getForm">Load Form</p-button> -->

        <br>

        <b-alert v-model="unsaved" variant="warning">
            <span>Form <b>{{deposit_form.form_id}}</b> has unsaved changes</span>
        </b-alert>

        <vue-json-editor v-model="deposit_form.content" :show-btns="true" @json-save="saveForm" @input="formChanged"></vue-json-editor>

    </div>
</template>

<script>
import axios from 'axios';
import vueJsonEditor from 'vue-json-editor'

export default {
    data() {
        return {
            deposit_form: {
                content: {
                    id: null
                }
            },
            unsaved: false
        }
    },
    components: {
        vueJsonEditor
    },
    mounted() {
        this.getForm();
    },
    methods: {
        getForm() {
            axios.get('../api/form', {params: {form_id: this.deposit_form.content.id || 'default'}})
            .then(response => {
                if (response.data.form) {
                    this.deposit_form.content = response.data.form.content;
                    console.log(response.data.form.content.id, 'loaded')
                }
            })
        },
        saveForm() {
            axios.post('../api/form', this.deposit_form)
            .then(response => {
                if (response.status == 200) {
                    this.unsaved = false;
                    this.$notify({
                        message: 'Form saved',
                        horizontalAlign: 'right',
                        verticalAlign: 'top',
                        type: 'success',
                        closeOnClick: true
                    });
                }            
            })
        },
        formChanged() {
            this.unsaved = true;
        }
    }
};
</script>
<style>
</style>